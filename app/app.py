import logging
from logging.handlers import RotatingFileHandler
from fastapi import FastAPI, HTTPException, Request, Depends
from pydantic import BaseModel, HttpUrl, conlist
from typing import List
import redis
import hashlib
from playwright.async_api import async_playwright, Browser
import os
import asyncio
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

import openai

# Environment variables
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
LOG_FILE = os.getenv('LOG_FILE', 'app.log')
LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', 5*1024*1024))
LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 5))

# Logging-Konfiguration mit RotatingFileHandler
log_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=LOG_MAX_BYTES,
    backupCount=LOG_BACKUP_COUNT
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        log_handler,
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# FastAPI-Initialisierung
app = FastAPI()

# OpenAI API Key setzen
openai.api_key = OPENAI_API_KEY

# Playwright Browser global initialisieren (nur eine Instanz für alle Anfragen)
playwright = None
browser = None

async def get_browser() -> Browser:
    global playwright, browser
    if playwright is None:
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=True)
    return browser

# Pydantic-Modell für die Anfrage
class UrlLists(BaseModel):
    urls_university_1: conlist(HttpUrl, min_items=1, max_items=10)
    urls_university_2: conlist(HttpUrl, min_items=1, max_items=10)

def generate_cache_key(url: str) -> str:
    """Erzeugt einen eindeutigen Schlüssel für die URL."""
    return hashlib.sha256(url.encode('utf-8')).hexdigest()

async def get_redis_client():
    return redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

async def scrape_content(url: str, browser: Browser, redis_client: redis.Redis) -> str:
    """ Holt den Textinhalt einer gegebenen URL mit Playwright, erweitertem Error-Handling und Redis-Caching. """
    cache_key = generate_cache_key(url)
    cached_content = await redis_client.get(cache_key)

    if cached_content:
        logger.info(f"Cache-Hit für URL: {url}")
        return cached_content.decode('utf-8')

    try:
        logger.info(f"Scraping gestartet für URL: {url} mit Playwright")
        page = await browser.new_page()
        
        # Optionale Optimierungen: Deaktiviere Bilder, CSS, etc.
        await page.route("**/*", lambda route, request: route.abort() if request.resource_type in ["image", "stylesheet", "font"] else route.continue_())
        
        await page.goto(url, timeout=60000)  # 60 Sekunden Timeout für langsame Seiten
        content = await page.content()  # Gesamter HTML-Inhalt der Seite
        await page.close()

        # Cache das Ergebnis in Redis
        await redis_client.setex(cache_key, 3600, content)  # Cache für 1 Stunde speichern

        logger.info(f"Scraping erfolgreich für URL: {url}")
        return content
    
    except Exception as e:
        logger.critical(f"Fehler beim Abrufen der URL mit Playwright: {url} - {str(e)}")
        raise HTTPException(status_code=500, detail=f"Fehler beim Abrufen der URL: {str(e)}")

async def compare_courses(content_1: str, content_2: str) -> str:
    """ Verwendet OpenAI um zwei Texte zu vergleichen. """
    try:
        logger.info("Vergleich der Kursinhalte gestartet")
        prompt = (
            f"Vergleiche die beiden folgenden Texte und bestimme, ob die Kursinhalte übereinstimmen:\n"
            f"Text 1:\n{content_1}\n\n"
            f"Text 2:\n{content_2}\n\n"
            f"Gib eine kurze Erklärung und einen Ähnlichkeitswert (0 bis 100) zurück."
        )
        response = openai.Completion.create(
            engine="text-davinci-003",  # Specify the model to use
            prompt=prompt,
            max_tokens=150
        )
        logger.info("Vergleich erfolgreich abgeschlossen")
        return response.choices[0].text.strip()

    except Exception as e:
        logger.critical(f"Fehler beim Vergleich der Kursinhalte: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ein Fehler ist beim Vergleich aufgetreten: {str(e)}")

@app.post("/compare-courses")
@RateLimiter(times=10, seconds=60)
async def compare_courses_endpoint(
    request: UrlLists,
    browser: Browser = Depends(get_browser),
    redis_client: redis.Redis = Depends(get_redis_client)
):
    try:
        logger.info("Empfangene Anfrage zur Kursanrechnung")

        # Inhalte von den URLs sammeln
        contents_university_1 = await asyncio.gather(*[scrape_content(str(url), browser, redis_client) for url in request.urls_university_1])
        contents_university_2 = await asyncio.gather(*[scrape_content(str(url), browser, redis_client) for url in request.urls_university_2])

        # Texte in einem String für jede Universität zusammenfassen
        text_university_1 = " ".join(contents_university_1)
        text_university_2 = " ".join(contents_university_2)

        # Vergleich durchführen
        comparison_result = await compare_courses(text_university_1, text_university_2)
        logger.info("Anfrage erfolgreich abgeschlossen")
        return {"comparison_result": comparison_result}

    except HTTPException as http_exc:
        logger.warning(f"HTTP-Fehler während der Anfrage: {http_exc.detail}")
        raise http_exc

    except Exception as e:
        logger.critical(f"Allgemeiner Fehler während der Anfrage: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Ein Fehler ist aufgetreten: {str(e)}")

@app.post("/invalidate-cache")
@RateLimiter(times=5, seconds=60)
async def invalidate_cache(
    url: HttpUrl,
    redis_client: redis.Redis = Depends(get_redis_client)
):
    """ Invalide den Cache für eine bestimmte URL. """
    try:
        cache_key = generate_cache_key(str(url))
        result = await redis_client.delete(cache_key)
        if result == 1:
            logger.info(f"Cache für URL erfolgreich invalidiert: {url}")
            return {"detail": f"Cache für URL {url} erfolgreich invalidiert."}
        else:
            logger.warning(f"Cache für URL nicht gefunden: {url}")
            return {"detail": f"Cache für URL {url} nicht gefunden oder bereits invalidiert."}
    except Exception as e:
        logger.critical(f"Fehler bei der Cache-Invalidierung für URL: {url} - {str(e)}")
        raise HTTPException(status_code=500, detail=f"Fehler bei der Cache-Invalidierung: {str(e)}")

# Schließen Sie den Playwright-Browser beim Beenden der Anwendung
@app.on_event("shutdown")
async def shutdown_event():
    global browser, playwright
    if browser:
        await browser.close()
    if playwright:
        await playwright.stop()

@app.on_event("startup")
async def startup():
    redis_client = await get_redis_client()
    await FastAPILimiter.init(redis_client)
