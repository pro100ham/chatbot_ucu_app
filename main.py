from fastapi import FastAPI, Request, Form, Query
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.LLM.ollama_client import OllamaClient
from app.LLM.openai_client import ChatGPTClient
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.integration.ticketService import CRMClient
import logging
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.sessionDB.models import Base
from app.sessionDB.database import async_session_maker, init_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.sessionDB.models import Message, Session
from app.utils.streaming import stream_response
from app.utils.auth import get_or_create_user_id
from app.LLM.chatgpt_web_client import ChatGPTWebClient

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

templates = Jinja2Templates(directory="app/templates")
widgets = Jinja2Templates(directory="app/widget")

client_ollama = OllamaClient()
client_chatgpt = ChatGPTClient()
client_chatgpt_web = ChatGPTWebClient()
crm_client = CRMClient()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

@app.on_event("startup")
async def load_model_on_startup():
    await init_db() 
    client_ollama.postCall()

@app.on_event("shutdown")
def shutdown_event():
    logger.info("Application shutdown")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    response = templates.TemplateResponse("index.html", {"request": request})
    get_or_create_user_id(request, response)
    return response

@app.get("/ask", response_class=JSONResponse)
async def ask(request: Request, question: str, model: str = Query("ollama")):
    client = get_llm_client(model)
    result = client.ask(question)
    if isinstance(result, dict):
        return JSONResponse(content=result)
    return JSONResponse(content={"answer": str(result)})

@app.post("/submit_crm_ticket", response_class=JSONResponse)
async def submit_crm_ticket(
    name: str = Form(...),
    email: str = Form(...),
    question: str = Form(...)
):
    crm_response = crm_client.forward_to_crm(question=question, answer="Користувач подав форму тікету.", user_email=email)
    return JSONResponse(content={"status": "success", "crm_response": crm_response})

@app.get("/intro")
async def intro(model: str = Query("ollama")):
    client = get_llm_client(model)
    return StreamingResponse(
        stream_response(client.preSessionConfiguration)(),
        media_type="text/event-stream"
    )

@app.get("/ask-stream")
async def ask_stream(request: Request, question: str, model: str = Query("ollama")):
    user_id = get_or_create_user_id(request)

    if model == "chatgpt":
        client = client_chatgpt
    if model == "chatgptweb":
        client = client_chatgpt_web
    else:
        client = client_ollama

    return StreamingResponse(
        stream_response(client.ask_stream, question, user_id, model)(),
        media_type="text/event-stream"
    )

@app.get("/pullmodel")
async def load_model():
    client_ollama.postCall()

@app.get("/widget", response_class=HTMLResponse)
async def chatbot_widget(request: Request):
    return widgets.TemplateResponse("widget.html", {"request": request})

@app.get("/testwidgetpage", response_class=HTMLResponse)
async def chatbot_widget(request: Request):
    return widgets.TemplateResponse("test_widget_page.html", {"request": request})

def get_llm_client(model: str):
    if model == "chatgpt":
        return client_chatgpt
    if model == "chatgptweb":
        return client_chatgpt_web
    else:
        return client_ollama
