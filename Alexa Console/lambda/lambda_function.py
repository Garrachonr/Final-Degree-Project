#Skill built by Alfredo Garrachon Ruiz

import logging
import json
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.dispatch_components import (AbstractRequestHandler, AbstractExceptionHandler, AbstractRequestInterceptor, AbstractResponseInterceptor)
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_dynamodb.adapter import DynamoDbAdapter
from ask_sdk_core.api_client import DefaultApiClient
import ask_sdk_core.utils as ask_utils

import os
import boto3

from ask_sdk_model import Response
from ask_sdk_model.ui import AskForPermissionsConsentCard
import pymongo
import random
from pymongo import MongoClient
from datetime import date

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

REQUIRED_PERMISSIONS = ["alexa::alerts:timers:skill:readwrite"]

#Timer 

def get_custom_task_launch_timer(duration, text, name, locale):
    return {
        "duration": duration,
        "timerLabel": name,
        "creationBehavior": {
            "displayExperience": {
                "visibility": "HIDDEN"
            }
        },
        "triggeringBehavior": {
            "operation": {
                "type": "ANNOUNCE",
                "textToAnnounce": [{
                    "locale": locale,
                    "text": text
                }]
            },
            "notificationConfig": {
                "playAudible": False
            }
        }
    }

#MongoDB        
client = MongoClient("mongodb+srv://garrachonr:129678@cluster0.p1uwe.mongodb.net/skill?retryWrites=true&w=majority")
x = client.Tomas
dbFacts = x.Facts
dbJokes = x.Jokes
dbEfemerides = x.Efemerides
dbWiki = x.Wiki
dbRiddles = x.Riddles
dbTrivial = x.Trivial

#Language
language = {
    'en-US': "en",
    'en-GB': "en",
    'en-CA': "en",
    'en-IN': "en",
    'en-AU': "en",
    'es-ES': "es"
}

# Defining the database region, table name and dynamodb persistence adapter
# Everything is extracted from the enviroment
ddb_region = os.environ.get('DYNAMODB_PERSISTENCE_REGION')
ddb_table_name = os.environ.get('DYNAMODB_PERSISTENCE_TABLE_NAME')
ddb_resource = boto3.resource('dynamodb', region_name=ddb_region)
dynamodb_adapter = DynamoDbAdapter(table_name=ddb_table_name, create_table=False, dynamodb_resource=ddb_resource)


class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        try:
            studies = persistent_attributes['studies']
            username = persistent_attributes['username']
            speak_output = random.choice(language_prompts["WELCOME_USER"]).format(username)
            ask_output = random.choice(language_prompts["REPROMPT"])
            
            #Restart If them have heard all.
            
            #Cuenta de los facts
            if len(persistent_attributes["countFact"]) > 20:
                countFact = [32]
                persistent_attributes["countFact"] = countFact
            #Cuenta de los chistes
            if len(persistent_attributes["countJoke"]) > 49:
                countJoke = [2]
                persistent_attributes["countJoke"] = countJoke
            #Cuenta de los howto
            if len(persistent_attributes["countWiki"]) > 14:
                countWiki = [2]
                persistent_attributes["countWiki"] = countWiki
            #Cuenta de los riddle
            if len(persistent_attributes["countRiddle"]) > 15:
                countRiddle = [2]
                persistent_attributes["countRiddle"] = countRiddle
            #Cuenta de los trivial
            if len(persistent_attributes["countTrivial"]) > 9:
                countTrivial = [2]
                persistent_attributes["countTrivial"] = countTrivial
            handler_input.attributes_manager.save_persistent_attributes()
        
        except:
            try:
                username = persistent_attributes['username']
                speak_output = random.choice(language_prompts["SECOND_TIME_USER"]).format(username)
                ask_output = random.choice(language_prompts["SECOND_TIME_USER_REPROMPT"])
            except:
                speak_output = random.choice(language_prompts["FIRST_TIME_USER"])
                ask_output = random.choice(language_prompts["FIRST_TIME_USER_REPROMPT"])

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(ask_output)
                .response
        )

#Handler para pruebas
class TryIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("TryIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        # get the countJoke
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        today = date.today()
        #d2 = today.strftime("%B %d, %Y")
        d2 = today.strftime("%B %d")
        speak_output = str(d2)

        return (
            handler_input.response_builder
                .speak(speak_output)
                .set_should_end_session(True)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )

#Handler para pruebas
class StudyIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("StudyIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        # get the countJoke
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        speak_output = random.choice(language_prompts["STUDY_TUTORIAL"]) + random.choice(language_prompts["KEEP"])
        ask_output = random.choice(language_prompts["REPROMPT"])

        return (
            handler_input.response_builder
                .speak(speak_output)
                #.set_should_end_session(True)
                .ask(ask_output)
                .response
        )

class TutorialIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("TutorialIntent")(handler_input)

    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        method = handler_input.request_envelope.request.intent.slots["method"].value
        if str(method) == "Pomodoro" or str(method) == "pomodoro":
            speak_output = random.choice(language_prompts["POMODORO"]) + random.choice(language_prompts["KEEP"])
            ask_output = random.choice(language_prompts["REPROMPT"])
        elif str(method) == "Gifford" or str(method) == "gifford" or str(method) == "Julia" or str(method) == "julia":
            speak_output = random.choice(language_prompts["GIFFORD"]) + random.choice(language_prompts["KEEP"])
            ask_output = random.choice(language_prompts["REPROMPT"])
        return (
            handler_input.response_builder
                .speak(speak_output)
                #.set_should_end_session(True)
                .ask(ask_output)
                .response
        )

#Handler para que puedo hacer
class WhatToDoIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("WhatToDoIntent")(handler_input)

    def handle(self, handler_input):
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        ask_output = random.choice(language_prompts["REPROMPT"])

        return (
            handler_input.response_builder
                .speak(ask_output)
                #.set_should_end_session(True)
                .ask(ask_output)
                .response
        )

#Handler para How To
class HowToIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("HowToIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        # get the countJoke
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        topic = handler_input.request_envelope.request.intent.slots["topic"].value
        if (str(topic) == "estudiar") or (str(topic) == "study"):
            topic = "Study"
        elif (str(topic) == "relax") or (str(topic) == "relajar") or (str(topic) == "relajación") or (str(topic) == "relajacion") or (str(topic) == "relajarme") or (str(topic) == "relajarse"):
            topic = "Relax"
        elif (str(topic) == "focus") or (str(topic) == "concentrar") or (str(topic) == "concentración") or (str(topic) == "concentracion") or (str(topic) == "concentrarme") or (str(topic) == "concentrarse"):
            topic = "Focus"
        elif (str(topic) == "learn") or (str(topic) == "aprender") or (str(topic) == "memorizar"):
            topic = "Learn"
        else:
            topic = "none"
            
        if topic == "none":
            speak_output = random.choice(language_prompts["NONE_HOWTO"]) + random.choice(language_prompts["KEEP"])
            ask_output = random.choice(language_prompts["NONE_HOWTO"]) + random.choice(language_prompts["KEEP"])
        else:
            #Sacar un howto del topic y sin repetirse
            countWiki = persistent_attributes['countWiki']
            flag = True
            while flag:
                n = random.randint(1,77)
                if n in countWiki:
                    flag = True
                elif dbWiki.find_one({"id": n})["topic"] != topic:
                    flag = True
                else:
                    flag = False
            countWiki.append(n)
            row = dbWiki.find_one({"id": n})
            persistent_attributes["countWiki"] = countWiki
            handler_input.attributes_manager.save_persistent_attributes()
            howto = row[random.choice(language_prompts["WIKI"])]
            speak_output = str(howto) + random.choice(language_prompts["KEEP"])
            ask_output = random.choice(language_prompts["REPROMPT"])

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(ask_output)
                .response
        )

#Handler para Efemerides de hoy
class EfemerideIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("EfemerideIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        today = date.today()
        d2 = today.strftime("%B ")
        d22 = today.strftime("%d")
        if d22[0] == "0":
            day = d22[1]
        else:
            day = d22
        row = dbEfemerides.find_one({"date": str(d2 + day).lower()})
        text = row[random.choice(language_prompts["EFEMERIDE"])]
        year = row["year"]
        speak_output = random.choice(language_prompts["EFEMERIDETODAY"]).format(year, text) + random.choice(language_prompts["KEEP"])
        ask_output = random.choice(language_prompts["REPROMPT"])
        return (
            handler_input.response_builder
                .speak(speak_output)
                #.set_should_end_session(True)
                .ask(ask_output)
                .response
        )

#Handler para Efemerides de cualquier dia
class EfemerideYearIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("EfemerideYearIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        day = handler_input.request_envelope.request.intent.slots["day"].value
        month = handler_input.request_envelope.request.intent.slots["month"].value
        monthEN = month
        #Translate moths
        if month == "enero":
            monthEN = "january"
        if month == "febrero":
            monthEN = "february"
        if month == "marzo":
            monthEN = "march"
        if month == "abril":
            monthEN = "april"
        if month == "mayo":
            monthEN = "may"
        if month == "junio":
            monthEN = "june"
        if month == "julio":
            monthEN = "july"
        if month == "agosto":
            monthEN = "august"
        if month == "septiembre":
            monthEN = "september"
        if month == "octubre":
            monthEN = "october"
        if month == "noviembre":
            monthEN = "november"
        if month == "diciembre":
            monthEN = "december"

        d2 = "{} {}".format(monthEN.lower(), day)
        row = dbEfemerides.find_one({"date": str(d2)})
        text = row[random.choice(language_prompts["EFEMERIDE"])]
        year = row["year"]
        speak_output = random.choice(language_prompts["EFEMERIDEYEAR"]).format(year, text) + random.choice(language_prompts["KEEP"])
        ask_output = random.choice(language_prompts["REPROMPT"])

        return (
            handler_input.response_builder
                .speak(speak_output)
                #.set_should_end_session(True)
                .ask(ask_output)
                .response
        )

class PomodoroIntentHandler(AbstractRequestHandler):
    """Handler for Pomodoro Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("PomodoroIntent")(handler_input)

    def handle(self, handler_input):
        #Miramos los permisos
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        permissions = handler_input.request_envelope.context.system.user.permissions
        if not (permissions and permissions.consent_token):
            return (
                handler_input.response_builder
                .speak(random.choice(language_prompts["TIMER_PERMISSIONS"]))
                .set_card(
                    AskForPermissionsConsentCard(permissions=REQUIRED_PERMISSIONS)
                )
                .response
            )
            
        #Sacamos 3 Facts y 1 chiste
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        countFact = persistent_attributes['countFact']
        studies = persistent_attributes["studies"]
        flag = True
        if studies == "General":
            flag3 = True
            flag = False
            while flag3:
                n = random.randint(1,99)
                m = random.randint(1,99)
                b = random.randint(1,99)
                if (n in countFact or m in countFact or b in countFact):
                    flag3 = True
                else:
                    flag3 = False
        while flag:
            n = random.randint(1,99)
            m = random.randint(1,99)
            b = random.randint(1,99)
            if (n in countFact or m in countFact or b in countFact):
                flag = True
            elif ((dbFacts.find_one({"id": n})["topic"] != studies) and (dbFacts.find_one({"id": m})["topic"] != studies) and (dbFacts.find_one({"id": b})["topic"] != studies)):
                flag = True
            else:
                flag = False
        countFact.append(n)
        countFact.append(m)
        countFact.append(b)
        row = dbFacts.find_one({"id": n})
        row3 = dbFacts.find_one({"id": m})
        row4 = dbFacts.find_one({"id": b})
        persistent_attributes["countFact"] = countFact

        
        countJoke = persistent_attributes['countJoke']
        flag2 = True
        while flag2:
            p = random.randint(1,50)
            if p in countJoke:
                flag2 = True
            else:
                flag2 = False
        countJoke.append(p)
        row2 = dbJokes.find_one({"id": p})
        persistent_attributes["countJoke"] = countJoke
        
        handler_input.attributes_manager.save_persistent_attributes()
        
        
        text = row[random.choice(language_prompts["FACTS"])]
        text2 = row2[random.choice(language_prompts["JOKES"])]
        text3 = row3[random.choice(language_prompts["FACTS"])]
        text4 = row4[random.choice(language_prompts["FACTS"])]
        
        #Ponemos el timer
        timer_service = handler_input.service_client_factory.get_timer_management_service()
        #Primero de 25 minutos
        timer_request = get_custom_task_launch_timer("PT25M", random.choice(language_prompts["BREAK"]).format(text), "Pomodoro_1", random.choice(language_prompts["LANGUAGE2"]))
        timer_response = timer_service.create_timer(timer_request)
        #Segundo de 5 minutos
        timer_request2 = get_custom_task_launch_timer("PT30M", random.choice(language_prompts["STUDY"]), "Pomodoro_2", random.choice(language_prompts["LANGUAGE2"]))
        timer_response2 = timer_service.create_timer(timer_request2)
        #Tercero de 25 minutos
        timer_request3 = get_custom_task_launch_timer("PT55M", random.choice(language_prompts["BREAK"]).format(text2), "Pomodoro_3", random.choice(language_prompts["LANGUAGE2"]))
        timer_response3 = timer_service.create_timer(timer_request3)
        #Cuarto de 5 minutos
        timer_request4 = get_custom_task_launch_timer("PT60M", random.choice(language_prompts["STUDY"]), "Pomodoro_4", random.choice(language_prompts["LANGUAGE2"]))
        timer_response4 = timer_service.create_timer(timer_request4)
        #Quinto de 25 minutos
        timer_request5 = get_custom_task_launch_timer("PT85M", random.choice(language_prompts["BREAK"]).format(text3), "Pomodoro_5", random.choice(language_prompts["LANGUAGE2"]))
        timer_response5 = timer_service.create_timer(timer_request5)
        #Sexto de 5 minutos
        timer_request6 = get_custom_task_launch_timer("PT90M", random.choice(language_prompts["STUDY"]), "Pomodoro_6", random.choice(language_prompts["LANGUAGE2"]))
        timer_response6 = timer_service.create_timer(timer_request6)
        #Septimo final
        timer_request7 = get_custom_task_launch_timer("PT115M", random.choice(language_prompts["POMODORO_END"]).format(text4), "Pomodoro_7", random.choice(language_prompts["LANGUAGE2"]))
        timer_response7 = timer_service.create_timer(timer_request7)
        
        if str(timer_response4.status) == "Status.ON":
            session_attr = handler_input.attributes_manager.session_attributes
            if not session_attr:
                session_attr['lastTimerId'] = timer_response.id
                speech_text = random.choice(language_prompts["POMODORO_RUNNING"])
        else:
            speech_text = random.choice(language_prompts["TIMER_ERROR"])

        return (
            handler_input.response_builder
            .speak(speech_text)
            .response
        )

class GiffordIntentHandler(AbstractRequestHandler):
    """Handler for Pomodoro Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("GiffordIntent")(handler_input)

    def handle(self, handler_input):
        #Miramos los permisos
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        permissions = handler_input.request_envelope.context.system.user.permissions
        if not (permissions and permissions.consent_token):
            return (
                handler_input.response_builder
                .speak(random.choice(language_prompts["TIMER_PERMISSIONS"]))
                .set_card(
                    AskForPermissionsConsentCard(permissions=REQUIRED_PERMISSIONS)
                )
                .response
            )
            
        #Sacamos 2 Facts y 1 chiste
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        countFact = persistent_attributes['countFact']
        studies = persistent_attributes["studies"]
        flag = True
        if studies == "General":
            flag3 = True
            flag = False
            while flag3:
                n = random.randint(1,99)
                if n in countFact:
                    flag3 = True
                else:
                    flag3 = False
        while flag:
            n = random.randint(1,99)
            if (n in countFact):
                flag = True
            elif (dbFacts.find_one({"id": n})["topic"] != studies):
                flag = True
            else:
                flag = False
        countFact.append(n)
        row = dbFacts.find_one({"id": n})
        persistent_attributes["countFact"] = countFact
        
        countJoke = persistent_attributes['countJoke']
        flag2 = True
        while flag2:
            p = random.randint(1,50)
            if p in countJoke:
                flag2 = True
            else:
                flag2 = False
        countJoke.append(p)
        row2 = dbJokes.find_one({"id": p})
        persistent_attributes["countJoke"] = countJoke
        
        handler_input.attributes_manager.save_persistent_attributes()
        
        
        text = row[random.choice(language_prompts["FACTS"])]
        text2 = row2[random.choice(language_prompts["JOKES"])]
        
        #Ponemos el timer
        timer_service = handler_input.service_client_factory.get_timer_management_service()
        #Primero de 52 minutos
        timer_request = get_custom_task_launch_timer("PT52M", random.choice(language_prompts["BREAK"]).format(text), "Julia_1", random.choice(language_prompts["LANGUAGE2"]))
        timer_response = timer_service.create_timer(timer_request)
        #Segundo de 17 minutos
        timer_request2 = get_custom_task_launch_timer("PT69M", random.choice(language_prompts["STUDY"]), "Julia_2", random.choice(language_prompts["LANGUAGE2"]))
        timer_response2 = timer_service.create_timer(timer_request2)
        #Tercero de 52 minutos
        timer_request3 = get_custom_task_launch_timer("PT2H", random.choice(language_prompts["BREAK"]).format(text2), "Julia_3", random.choice(language_prompts["LANGUAGE2"]))
        timer_response3 = timer_service.create_timer(timer_request3)
        
        if str(timer_response2.status) == "Status.ON":
            session_attr = handler_input.attributes_manager.session_attributes
            if not session_attr:
                session_attr['lastTimerId'] = timer_response.id
                speech_text = random.choice(language_prompts["JULIA_RUNNING"])
        else:
            speech_text = random.choice(language_prompts["TIMER_ERROR"])

        return (
            handler_input.response_builder
            .speak(speech_text)
            .response
        )

class RiddleIntentHandler(AbstractRequestHandler):
    """Handler for Timer Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("RiddleIntent")(handler_input)

    def handle(self, handler_input):
        #Miramos los permisos
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        permissions = handler_input.request_envelope.context.system.user.permissions
        if not (permissions and permissions.consent_token):
            return (
                handler_input.response_builder
                .speak(random.choice(language_prompts["TIMER_PERMISSIONS"]))
                .set_card(
                    AskForPermissionsConsentCard(permissions=REQUIRED_PERMISSIONS)
                )
                .response
            )
        #Sacamos el Riddle
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        #If there is no topic selected
        countRiddle = persistent_attributes['countRiddle']
        flag = True
        while flag:
            n = random.randint(0,17)
            if n in countRiddle:
                flag = True
            else:
                flag = False
            countRiddle.append(n)
        row = dbRiddles.find_one({"id": n})
        persistent_attributes["countRiddle"] = countRiddle
        handler_input.attributes_manager.save_persistent_attributes()
        
        text = row[random.choice(language_prompts["RIDDLE_ANSWER"])]
        #Ponemos el timer
        timer_service = handler_input.service_client_factory.get_timer_management_service()
        timer_request = get_custom_task_launch_timer("PT10S", random.choice(language_prompts["ANSWER_RIDDLE"]).format(text), "Riddle", random.choice(language_prompts["LANGUAGE2"]))
        timer_response = timer_service.create_timer(timer_request)
        
        if str(timer_response.status) == "Status.ON":
            session_attr = handler_input.attributes_manager.session_attributes
            if not session_attr:
                session_attr['lastTimerId'] = timer_response.id
                speech_text = row[random.choice(language_prompts["RIDDLE_QUESTION"])]
        else:
            speech_text = random.choice(language_prompts["RIDDLE_ERROR"])
        return (
            handler_input.response_builder
            .speak(speech_text)
            .response
        )

class SetTimerIntentHandler(AbstractRequestHandler):
    """Handler for Timer Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("SetTimerIntent")(handler_input)

    def handle(self, handler_input):
        #Miramos los permisos
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        permissions = handler_input.request_envelope.context.system.user.permissions
        if not (permissions and permissions.consent_token):
            return (
                handler_input.response_builder
                .speak(random.choice(language_prompts["TIMER_PERMISSIONS"]))
                .set_card(
                    AskForPermissionsConsentCard(permissions=REQUIRED_PERMISSIONS)
                )
                .response
            )
        #Sacamos el Fact
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        #If there is no topic selected
        try:
            studies = persistent_attributes['studies']
            countFact = persistent_attributes['countFact']
            flag = True
            if studies == "General":
                flag2 = True
                flag = False
                while flag2:
                    n = random.randint(1,99)
                    if n in countFact:
                        flag2 = True
                    else:
                        flag2 = False
            while flag:
                n = random.randint(1,99)
                if n in countFact:
                    flag = True
                elif dbFacts.find_one({"id": n})["topic"] != studies:
                    flag = True
                else:
                    flag = False
                countFact.append(n)
            row = dbFacts.find_one({"id": n})
            persistent_attributes["countFact"] = countFact
            handler_input.attributes_manager.save_persistent_attributes()
            
            text = "Es un placer escucharte otra vez, aquí tienes un dato curioso, {}".format(row[random.choice(language_prompts["FACTS"])])
            name = "Timer Fact"
            #Ponemos el timer
            duration_slot_value = ask_utils.get_slot_value(handler_input, 'duration')
            timer_request = get_custom_task_launch_timer(duration_slot_value, text, name, random.choice(language_prompts["LANGUAGE2"]))
            timer_service = handler_input.service_client_factory.get_timer_management_service()
            timer_response = timer_service.create_timer(timer_request)
            
            if str(timer_response.status) == "Status.ON":
                session_attr = handler_input.attributes_manager.session_attributes
                if not session_attr:
                    session_attr['lastTimerId'] = timer_response.id
                    speech_text = random.choice(language_prompts["TIMER_RUNNING"])
            else:
                speech_text = random.choice(language_prompts["TIMER_ERROR"])
            
        #Don´t wait por an answer    
            flagAsk = True
                
        except:
            flagAsk = False
            speech_text = random.choice(language_prompts["STUDIES_ERROR"])
            ask_output = random.choice(language_prompts["STUDIES_ERROR_REPROMPT"])

        if flagAsk:
            return (
                handler_input.response_builder
                .speak(speech_text)
                .response
            )
        else:
            return (
                handler_input.response_builder
                .speak(speech_text)
                .ask(ask_output)
                .response
            )

#Take the name from the request and save it 
class NewNameIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("NewNameIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        username = handler_input.request_envelope.request.intent.slots["UserNameSlot"].value
        persistent_attributes["username"] = username
            #Cuenta de los facts
        countFact = [32]
        persistent_attributes["countFact"] = countFact
            #Cuenta de los chistes
        countJoke = [2]
        persistent_attributes["countJoke"] = countJoke
            #Cuenta de los howto
        countWiki = [2]
        persistent_attributes["countWiki"] = countWiki
        #Cuenta de los riddle
        countRiddle = [2]
        persistent_attributes["countRiddle"] = countRiddle
        #Cuenta de los trivial
        countTrivial = [2]
        persistent_attributes["countTrivial"] = countTrivial
        #trivial
        persistent_attributes["questionTrivial"] = ""
            # Write user's name to the DB.
        handler_input.attributes_manager.save_persistent_attributes()

        try:
            studies = persistent_attributes['studies']
            if (str(username) == "Claudia" or str(username) == "claudia"):
                speak_output="Bienvenida Claudia, sabes que la canción favorita de Taylor de todo su repertorio es All too well?. Bueno, pideme lo que quieras"
                ask_output = random.choice(language_prompts["NEW_NAME_REPROMPT"])
            elif (str(username) == "Irene" or str(username) == "irene"):
                speak_output="Bienvenida Irene, sabes que la primera referencia al crochet data del 1821 en un libro de Elizabeth Grant? . Bueno, pideme lo que quieras"
                ask_output = random.choice(language_prompts["NEW_NAME_REPROMPT"])
            elif (str(username) == "Sergio" or str(username) == "sergio"):
                speak_output="No tienes permisos para utilizar al lazarillo Tomás, necesitas reemitir una carta firmada por Ana Botín a fernandez de los rios 82 3 A Derecha"
                ask_output = "No tienes permisos para utilizar al lazarillo Tomás, necesitas reemitir una carta firmada por Ana Botín a fernandez de los rios 82 3 A Derecha"
            else:
                speak_output = random.choice(language_prompts["NEW_NAME2"]).format(username)
                ask_output = random.choice(language_prompts["NEW_NAME_REPROMPT2"])
        except:
            if (str(username) == "Claudia" or str(username) == "claudia"):
                speak_output="Bienvenida Claudia, sabes que la canción favorita de Taylor de todo su repertorio es All too well?. Bueno, continuemos, di que tu campo de estudio es tecnología para ajustar tus gustos"
                ask_output = random.choice(language_prompts["NEW_NAME_REPROMPT"])
            elif (str(username) == "Irene" or str(username) == "irene"):
                speak_output="Bienvenida Irene, sabes que la primera referencia al crochet data del 1821 en un libro de Elizabeth Grant? . Bueno, continuemos, di que tu campo de estudio es tecnología para ajustar tus gustos"
                ask_output = random.choice(language_prompts["NEW_NAME_REPROMPT"])
            elif (str(username) == "Sergio" or str(username) == "sergio"):
                speak_output="No tienes permisos para utilizar al lazarillo Tomás, necesitas reemitir una carta firmada por Ana Botín a fernandez de los rios 82 3 A Derecha"
                ask_output = "No tienes permisos para utilizar al lazarillo Tomás, necesitas reemitir una carta firmada por Ana Botín a fernandez de los rios 82 3 A Derecha"
            else:
                speak_output=random.choice(language_prompts["NEW_NAME"]).format(username)
                ask_output = random.choice(language_prompts["NEW_NAME_REPROMPT"])

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .set_should_end_session(True)
                .ask(ask_output)
                .response
        )

#Take the studies field from the request and save it 
class StudiesIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("StudiesIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        
        try:
            username = persistent_attributes['username']
            studies = handler_input.request_envelope.request.intent.slots["studies"].value
            
            #Select studies
            
            if (str(studies) == "tecnologia") or (str(studies) == "technology") or (str(studies) == "tech") or (str(studies) == "tecnología"):
                studies2 = "Tech"
            elif (str(studies) == "health") or (str(studies) == "salud") or (str(studies) == "sanitario"):
                studies2 = "Health"
            elif (str(studies) == "law") or (str(studies) == "legal") or (str(studies) == "derecho"):
                studies2 = "Law"
            elif (str(studies) == "general"):
                studies2 = "General"
            
            persistent_attributes["studies"] = studies2
            handler_input.attributes_manager.save_persistent_attributes()
            speak_output = random.choice(language_prompts["NEW_STUDIES"]).format(studies)
            ask_output = random.choice(language_prompts["NEW_STUDIES_REPROMPT"])
        except:
            speak_output = random.choice(language_prompts["NEW_STUDIES2"])
            ask_output = random.choice(language_prompts["NEW_STUDIES_REPROMPT2"])

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .set_should_end_session(True)
                .ask(ask_output)
                .response
        )

#Lanzamos un FACT
class FactIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("FactIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        # get the countFact
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        try:
            studies = persistent_attributes['studies']
            countFact = persistent_attributes['countFact']
            flag = True
            if studies == "General":
                flag2 = True
                flag = False
                while flag2:
                    n = random.randint(1,99)
                    if n in countFact:
                        flag2 = True
                    else:
                        flag2 = False
            while flag:
                n = random.randint(1,99)
                if n in countFact:
                    flag = True
                elif dbFacts.find_one({"id": n})["topic"] != studies:
                    flag = True
                else:
                    flag = False
            countFact.append(n)
            row = dbFacts.find_one({"id": n})
            persistent_attributes["countFact"] = countFact
            handler_input.attributes_manager.save_persistent_attributes()
            speak_output = row[random.choice(language_prompts["FACTS"])] + random.choice(language_prompts["KEEP"])
            ask_output = random.choice(language_prompts["REPROMPT"])
            #Don´t wait for an answer
            flagAsk = True
        except:
            flagAsk = False
            speak_output = random.choice(language_prompts["STUDIES_ERROR"])
            ask_output = random.choice(language_prompts["STUDIES_ERROR_REPROMPT"])
        
        if flagAsk:
            return (
                handler_input.response_builder
                    .speak(speak_output)
                    .ask(ask_output)
                    .response
            )
        else:
            return (
                handler_input.response_builder
                    .speak(speak_output)
                    .ask(ask_output)
                    .response
            )

#Lanzamos un Joke
class JokeIntentHandler(AbstractRequestHandler):
    """Handler for Hello World Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("JokeIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        # get the countJoke
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        countJoke = persistent_attributes['countJoke']
        flag = True
        while flag:
            n = random.randint(1,19)
            if n in countJoke:
                flag = True
            else:
                flag = False
        countJoke.append(n)
        row = dbJokes.find_one({"id": n})
        persistent_attributes["countJoke"] = countJoke
        handler_input.attributes_manager.save_persistent_attributes()
        # number = random.randint(1,115)
        #row = dbFacts.find_one({"id": number})
        speak_output = row[random.choice(language_prompts["JOKES"])] + random.choice(language_prompts["KEEP"])
        ask_output = random.choice(language_prompts["REPROMPT"])

        return (
            handler_input.response_builder
                .speak(speak_output)
                #.set_should_end_session(True)
                .ask(ask_output)
                .response
        )

#Lanzamos el trivial
class TrivialIntentHandler(AbstractRequestHandler):

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("TrivialIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        # get the countJoke
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        if persistent_attributes["questionTrivial"] == "":
            countTrivial = persistent_attributes['countTrivial']
            flag = True
            while flag:
                n = random.randint(0,11)
                if n in countTrivial:
                    flag = True
                else:
                    flag = False
            countTrivial.append(n)
            row = dbTrivial.find_one({"id": n})
            persistent_attributes["countTrivial"] = countTrivial
            persistent_attributes["questionTrivial"] = row[random.choice(language_prompts["TRIVIAL_QUESTION"])]
            persistent_attributes["answerTrivial"] = row[random.choice(language_prompts["TRIVIAL_ANSWER"])]
            handler_input.attributes_manager.save_persistent_attributes()

            speak_output = row[random.choice(language_prompts["TRIVIAL_QUESTION"])]
        else:
            speak_output = persistent_attributes["questionTrivial"]

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class AnswerTrivialIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AnswerTrivialIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        answer = handler_input.request_envelope.request.intent.slots["answer"].value
        if persistent_attributes["answerTrivial"] == "":
            speak_output = random.choice(language_prompts["TRIVIAL_MISSING"])
        else:
            persistent_attributes["questionTrivial"] = ""
            #Check de answer
            
            if ((str(answer) == "primero") or (str(answer) == "uno") or (str(answer) == "one") or (str(answer) == "1") or (str(answer) == "1.º") or (str(answer) == "first") or (str(answer) == "1st")):
                answer2 = "1"
            elif ((str(answer) == "segundo") or (str(answer) == "dos") or (str(answer) == "two") or (str(answer) == "2") or (str(answer) == "2.º") or (str(answer) == "second") or (str(answer) == "2nd")):
                answer2 = "2"
            elif ((str(answer) == "tercero") or (str(answer) == "tres") or (str(answer) == "three") or (str(answer) == "3") or (str(answer) == "3.º") or (str(answer) == "third ")  or (str(answer) == "3rd")):
                answer2 = "3"
            elif ((str(answer) == "cuarto") or (str(answer) == "cuatro") or (str(answer) == "four") or (str(answer) == "4") or (str(answer) == "4.º") or (str(answer) == "fourth") or (str(answer) == "4th")):
                answer2 = "4"
            else:
                answer2 = "none"

            if answer2 == "none":
                speak_output = str(answer)
                ask_output = random.choice(language_prompts["NONE_TRIVIAL"])
            else:
                answer = persistent_attributes["answerTrivial"]
                if answer[0] == answer2:
                    speak_output = random.choice(language_prompts["TRIVIAL_CORRECT"]) + random.choice(language_prompts["KEEP"])
                else:
                    speak_output = random.choice(language_prompts["TRIVIAL_WRONG"]).format(answer) + random.choice(language_prompts["KEEP"])
                handler_input.attributes_manager.save_persistent_attributes()
                ask_output = random.choice(language_prompts["REPROMPT"])
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(ask_output)
                .response
        )

class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        try:
            studies = persistent_attributes['studies']
            username = persistent_attributes['username']
            speak_output = random.choice(language_prompts["HELP"]).format(username)
            ask_output = random.choice(language_prompts["HELP"])
        except:
            try:
                username = persistent_attributes['username']
                speak_output = random.choice(language_prompts["SECOND_TIME_USER"]).format(username)
                ask_output = random.choice(language_prompts["SECOND_TIME_USER_REPROMPT"])
            except:
                speak_output = random.choice(language_prompts["FIRST_TIME_USER"])
                ask_output = random.choice(language_prompts["FIRST_TIME_USER_REPROMPT"])

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        speak_output = random.choice(language_prompts["BYE"])

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        logger.info("In FallbackIntentHandler")
        speech = random.choice(language_prompts["FALLBACK"])
        reprompt = random.choice(language_prompts["FALLBACK_REPROMPT"])

        return handler_input.response_builder.speak(speech).ask(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        speak_output = random.choice(language_prompts["EXCEPTION"])

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# This interceptor is used for supporting different languages and locales. It detects the users locale,
# loads the corresponding language prompts and sends them as a request attribute object to the handler functions.
class LocalizationInterceptor(AbstractRequestInterceptor):

    def process(self, handler_input):
        locale = handler_input.request_envelope.request.locale
        logger.info("Locale is {}".format(locale))
        local = language[str(locale)]
        logger.info("Locale is {}".format(local))

        try:
            with open("languages/"+local+".json") as language_data:
                language_prompts = json.load(language_data)
        except:
            with open("languages/"+ local+".json") as language_data:
                language_prompts = json.load(language_data)
        
        handler_input.attributes_manager.request_attributes["_"] = language_prompts


# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = CustomSkillBuilder(persistence_adapter = dynamodb_adapter, api_client=DefaultApiClient())

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(TryIntentHandler())
sb.add_request_handler(WhatToDoIntentHandler())
sb.add_request_handler(TutorialIntentHandler())
sb.add_request_handler(StudyIntentHandler())
sb.add_request_handler(EfemerideIntentHandler())
sb.add_request_handler(HowToIntentHandler())
sb.add_request_handler(EfemerideYearIntentHandler())
sb.add_request_handler(RiddleIntentHandler())
sb.add_request_handler(TrivialIntentHandler())
sb.add_request_handler(AnswerTrivialIntentHandler())
sb.add_request_handler(GiffordIntentHandler())
sb.add_request_handler(PomodoroIntentHandler())
sb.add_request_handler(SetTimerIntentHandler())
sb.add_request_handler(StudiesIntentHandler())
sb.add_request_handler(NewNameIntentHandler())

sb.add_request_handler(FactIntentHandler())
sb.add_request_handler(JokeIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

sb.add_global_request_interceptor(LocalizationInterceptor())

lambda_handler = sb.lambda_handler()