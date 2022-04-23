# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
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

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

REQUIRED_PERMISSIONS = ["alexa::alerts:timers:skill:readwrite"]

#Timer 

def get_custom_task_launch_timer(duration, text):
    return {
        "duration": duration,
        "timerLabel": "My Task Timer",
        "creationBehavior": {
            "displayExperience": {
                "visibility": "HIDDEN"
            }
        },
        "triggeringBehavior": {
            "operation": {
                "type": "ANNOUNCE",
                "textToAnnounce": [{
                    "locale": "en-US",
                    "text": "Es un placer escucharte otra vez, aquí tienes un dato curioso, {}".format(text)
                }]
            },
            "notificationConfig": {
                "playAudible": False
            }
        }
    }

#MongoDB        
client = MongoClient("mongodb+srv://garrachonr:129678@cluster0.p1uwe.mongodb.net/skill?retryWrites=true&w=majority")
x = client.skill
db = x.facts

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
            username = persistent_attributes['username']
            speak_output = random.choice(language_prompts["WELCOME_USER"]).format(username)
            ask_output = random.choice(language_prompts["WELCOME_USER_REPROMPT"])
        except:
            speak_output = random.choice(language_prompts["FIRST_TIME_USER"])
            ask_output = random.choice(language_prompts["FIRST_TIME_USER_REPROMPT"])

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(ask_output)
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
        count = persistent_attributes['count']
        flag = True
        while flag:
            n = random.randint(1,115)
            if n in count:
                flag = True
            else:
                flag = False
        count.append(n)
        row = db.find_one({"id": n})
        persistent_attributes["count"] = count
        handler_input.attributes_manager.save_persistent_attributes()
        # number = random.randint(1,115)
        #row = db.find_one({"id": number})
        text = row[random.choice(language_prompts["FACTS"])]
        
        #Ponemos el timer
        duration_slot_value = ask_utils.get_slot_value(handler_input, 'duration')
        timer_request = get_custom_task_launch_timer(duration_slot_value, text)
        timer_service = handler_input.service_client_factory.get_timer_management_service()
        timer_response = timer_service.create_timer(timer_request)
        
        if str(timer_response.status) == "Status.ON":
            session_attr = handler_input.attributes_manager.session_attributes
            if not session_attr:
                session_attr['lastTimerId'] = timer_response.id
                speech_text = random.choice(language_prompts["TIMER_RUNNING"])
        else:
            speech_text = random.choice(language_prompts["TIMER_ERROR"])

        return (
            handler_input.response_builder
            .speak(speech_text)
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
        try:
            username = persistent_attributes['username']
            speak_output = random.choice(language_prompts["FALLBACK"])
            ask_output = random.choice(language_prompts["NEW_NAME_REPROMPT"])
        except:
            username = handler_input.request_envelope.request.intent.slots["UserNameSlot"].value
            persistent_attributes["username"] = username
            count = [32, 54]
            persistent_attributes["count"] = count
            # Write user's name to the DB.
            handler_input.attributes_manager.save_persistent_attributes()
            speak_output=random.choice(language_prompts["NEW_NAME"]).format(username)
            ask_output = random.choice(language_prompts["NEW_NAME_REPROMPT"])

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
        # get the count
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        count = persistent_attributes['count']
        flag = True
        while flag:
            n = random.randint(1,115)
            if n in count:
                flag = True
            else:
                flag = False
        count.append(n)
        row = db.find_one({"id": n})
        persistent_attributes["count"] = count
        handler_input.attributes_manager.save_persistent_attributes()
        # number = random.randint(1,115)
        #row = db.find_one({"id": number})
        speak_output = row[random.choice(language_prompts["FACTS"])]

        return (
            handler_input.response_builder
                .speak(speak_output)
                .set_should_end_session(True)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        language_prompts = handler_input.attributes_manager.request_attributes["_"]
        persistent_attributes = handler_input.attributes_manager.persistent_attributes
        try:
            username = persistent_attributes['username']
            speak_output = random.choice(language_prompts["WELCOME_USER_REPROMPT"])
            ask_output = random.choice(language_prompts["WELCOME_USER_REPROMPT"])
        except:
            speak_output = random.choice(language_prompts["FIRST_TIME_USER_REPROMPT"])
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
        speak_output = "Goodbye!"

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

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

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
sb.add_request_handler(SetTimerIntentHandler())
sb.add_request_handler(NewNameIntentHandler())
sb.add_request_handler(FactIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())

sb.add_global_request_interceptor(LocalizationInterceptor())

lambda_handler = sb.lambda_handler()