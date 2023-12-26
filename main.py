from tkinter import *
from PIL import ImageTk, Image

import speech_recognition as sr
import mysql.connector as m
import threading as th
import datetime, pyttsx3, webbrowser, random, os
try:
  import wikipedia
except ImportError: wikipedia = None


state = False

k = m.connect(user="root", password="tiger123", database="Friday")
c = k.cursor()

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty("voice", voices[7].id)

engine.startLoop(False)

queue = []
Lok = th.Lock()

def turnoff():
  global state
  state = False

  lel.config(text="not listening")
  sbun.set("Start")

def rnw(text):
  engine.say(text)
  engine.iterate()

def speak(text):
  th.Thread(target=rnw, args=(text,)).start()


def mech(query):
  global state

  with Lok:
    if not state:
      return
  if not len(queue) == 0:
    return

  greetings = ("hello Mukesh", "Hi Mukesh", "What's Up?", "How can i help?", "Go ahead... I'm Listening")
  Jokes = (
    "Why can't a nose be 12 inches long?..., Because then it would be a foot..., hahaha",
    "What do sprinters eat before a race?..., Nothing, they fast!...hahaha",
    "Can February march?... No, but April may!",
    "My uncle named his dogs Rolex and Timex..., They're his watch dogs!",
    "What did the policeman say to his belly button?, You're under a vest!" )
  Timeout = (
    "Bye Bye",
    "",
    "See ya",
    "Goodtime",
    "Bye",
    "Have a greatday" )
  uc = (
    "wrong command",
    "unknown command",
    "Try again",
    "i'm not sure what that is",
    "what does that mean?" )

  sites = {
    "youtube": "https://youtube.com",
    "google": "https://google.com",
    "apple": "https://apple.com",
    "pinterest": "https://in.pinterest.com",
    "medium": "https://medium.com",
    "behance": "https://behance.net",
    "prime video": "https://primevideo.com",
    "hotstar": "https://hotstar.com"
  }

  if query in ("quit", "bye", "bye bye", "thank you", "thanks for now", "goodnight", "Nevermind"):
      speak(random.choice(Timeout))
      return

  if "who is" in query or "wikipedia" in query:
      speak("searching wikipedia... Please Wait")
      query = query.replace("wikipedia", "")
      try:
        results = wikipedia.summary(query, sentences=2)
      except: results=""
      speak(results)

  elif query.startswith("open "):
      k = os.system("open -a '{}'".format(query[5:].strip()))

      if k == 256:
          speak("no app found")
          speak("looking for the website")
          try:
              webbrowser.open(sites[query.split()[1]])
          except KeyError:
              speak("I couldn't find the site either, here are search results")
              webbrowser.open( "https://google.com/search?q={}".format('+'.join(query.split()[1:])))

  elif query.startswith("search "):
      speak("Here's what i Found")
      webbrowser.open("https://google.com/search?q={}".format('+'.join(query.split()[1:])) )

  elif query.startswith("add contact") or query.startswith("save contact") or query.startswith("new contact") or query.startswith("add a contact") or query.startswith("contact"):
      speak("tell me the name")
      name = Command().strip().lower()

      speak("tell me the number")
      phoneno = Command().strip().lower()

      c.execute("select * from contacts")
      try:
          ln = c.fetchall()
      except: ln = ()

      try:
          c.execute("insert into contacts values ({}, {}, {})".format(max(ln, key=lambda a: a[0])[0] + 1, repr(name), phoneno.replace(' ', '')) )
          k.commit()

          speak("saved successfully")
      except m.errors.IntegrityError: speak("EXISTS")

  elif query.startswith("find contact") or query.startswith("show contact named"):
      name = query[len("find contact"):].strip()
      c.execute("select * from contacts where name={}".format(repr(name)) )
      try:
          rs = c.fetchall()
          print(rs)

          if (len(rs) > 1):
              speak("found more than one")
          else:
              speak("number is {}".format(' '.join(list(str(rs[0][2])))) )
      except: speak("found no contact matches")

  elif query.startswith("delete contact") or query.startswith("remove contact"):
      name = query[len("delete contact"):].strip()
      try:
          c.execute("delete from contacts where name={}".format(repr(name)))
          speak("successfully deleted")
      except:
          pass

  elif query in ("show all contacts", "show me my contacts", "show me all contacts", "show contacts friday", "Contacts"):
      speak("here you go, Mukesh")
      c.execute("select * from contacts")
      rs = c.fetchall()
      print(rs)

  elif "news" in query:
      speak("your daily news is here")
      webbrowser.open("https://news.google.com/topstories?")

  elif query in ("hey", "hello", "hi friday", "hello friday"):
      speak(random.choice(greetings))

  elif "time" in query:
      strTime = datetime.datetime.now().strftime("%I:%M:%S")
      speak("the time is {}".format(strTime))

  elif query in ('how are you doing', 'what are you doing'):
      speak("Just Learning New things, Master!")

  elif query in ("tell me a joke", "joke"):
      speak(random.choice(Jokes))

  else:
      speak(random.choice(uc))


  turnoff()
  k.commit()


def Command():
    global queue
    r = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")
        audio = r.listen(source)
    try:
      with Lok:
        if state:
          print("Recognizing...")
          speak("recognizing")
          query = r.recognize_google(audio, language='en-in')
          print(f"user said:{query}\n")

    except Exception as e:
        query = None

    del queue[0]
    return query

def cmd():
  try:
    queue.append(True)
    return mech(Command().lower())
  except: return ""

def main(e=None):
  global state

  state = not state
  if state: # Start
    lel.config(text="Listening...")
    sbun.set("Stop")

    speak("listening")

    th.Thread(target=cmd).start()

  else: # Stop
    turnoff()
    speak("not listening")

  w.update()

try:
  w = Tk()
  w.title("Friday")
  w.geometry("900x660")
  w.configure(bg="#180C35")
  # w.resizable(0,0)

  image = ImageTk.PhotoImage(Image.open("main.png").resize((900,510)) )
  fmain = Label(w, image=image)
  fmain.pack()

  lel = Label(w, text="not listening",font=("optima",30),bg="#180C35",fg="White")
  lel.pack()

  sbun = StringVar()
  bun = Button(w,textvariable=sbun,fg="black",font=("Optima",20),padx=80,pady=10,borderwidth=0, command=main)
  sbun.set("Start")
  bun.pack()

  w.bind("<Key-space>", main)
  w.mainloop()
finally:
  print("closing")
  engine.endLoop()
