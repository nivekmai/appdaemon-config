from __future__ import print_function
import datetime
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import appdaemon.plugins.hass.hassapi as hass

SCOPES = ["https://www.googleapis.com/auth/calendar"]
TAG = "CalendarSwitch"


class CalendarSwitch(hass.Hass):
    """
    Turn switches on and off at specific times if the trigger times are within offset_hours of a named event on a specific calendar.

    To set up the token, set up the google calender integration: https://www.home-assistant.io/integrations/calendar.google/. Point "token" to your ".google.token" file in your home assistant directory.

    The python libraries used in the quickstart guide are necessary to have installed in the environment that appdaemon runs in.

    This app operates in UTC time.
    """

    def initialize(self):
        # Times, defined as a comma separated list of time strings
        on_times = self.split_device_list(self.args["on_times"])
        off_times = self.split_device_list(self.args["off_times"])
        # Switches, defined as a comma separated list
        self.switches = self.split_device_list(self.args["switches"])
        self.speakers = self.split_device_list(self.args.get("speakers", ""))
        self.debug_speaker = self.args.get("debug_speaker")
        # Phrases to be spoken when turning on or off switches, leave empty to
        # not speak
        self.on_phrase = self.args.get("on_phrase")
        self.off_phrase = self.args.get("off_phrase")
        # Authentication files
        self.TOKEN_FILE = self.args.get("token")
        # Which calendar to look for events in
        self.CALENDAR_ID = self.args.get("calendar")
        # Event name (case insensitive) to look for
        self.event_name = self.args.get("event")
        # How many hours ahead of event start time can switches trigger in
        self.offset_hours = self.args.get("offset_hours")

        if not self.CALENDAR_ID or not self.TOKEN_FILE:
            self.log(
                TAG
                + " invalid config, 'token' and 'calendar' must be set",
                level="ERROR",
            )
            return

        self.log(TAG + " init: {}".format(self.__dict__))

        self.run_every(self.every_hour, "now", 60 * 60)

        if self.events_in_range():
            self.log(TAG + " events in range from start")


        for on_time in on_times:
            time = self.parse_time(on_time)
            self.run_daily(self.turn_on_switches, time)
        for off_time in off_times:
            time = self.parse_time(off_time)
            self.run_daily(self.turn_off_switches, time)

    def every_hour(self, kwargs):
        self.log(TAG + " trying to get calendar events")
        try:
            self.get_events()
            # self.log(TAG + " success")
        except:
            if self.debug_speaker is not None:
                self.log(TAG + " failed to get calendar events")
                self.call_service(
                    "tts/google_say", entity_id=self.debug_speaker, message="failed to get events for Calendar Switch"
                )

    def get_service(self):
        """Get a service client, log in or refresh credentials if necessary"""
        creds = None
        if os.path.exists(self.TOKEN_FILE):
            creds = Credentials.from_authorized_user_file(self.TOKEN_FILE, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                raise Exception("token invalid")
                # flow = InstalledAppFlow.from_client_secrets_file(
                #     self.CREDENTIAL_FILE, SCOPES
                # )
                #creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self.TOKEN_FILE, "w") as token:
                token.write(creds.to_json())

        return build("calendar", "v3", credentials=creds)

    def get_events(self):
        """Get a clean list of events from the calendar API"""
        service = self.get_service()
        now = datetime.datetime.utcnow().isoformat() + "Z"
        events_result = (
            service.events()
            .list(
                calendarId=self.CALENDAR_ID,
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        return events_result.get("items", [])

    def events_in_range(self):
        """Check if any events are in range of current time"""
        if self.event_name:
            for event in self.get_events():
                if self.event_matches(event):
                    return True
            return False
        return True

    def event_matches(self, event):
        """Check if an event starts within the offset_hours after the current time"""
        self.log(TAG + " check event: " + event["summary"].lower())
        if event["summary"].lower() == self.event_name.lower():
            event_start = self.parse_event_time(event)
            if event_start is None:
                self.log(TAG + " None event")
            else:
                self.log(
                    TAG + " event start " + event_start.strftime("%Y-%m-%dT%H:%M:%S")
                )
            if (
                event_start - datetime.timedelta(hours=self.offset_hours)
                < datetime.datetime.utcnow()
            ):
                return True
            else:
                self.log(TAG + " outside range")
        else:
            self.log(TAG + " name mismatch")
        return False

    def parse_event_time(self, event):
        """Parse google calendar event time (iso format), fallback to day granularity"""
        try:
            start_date = datetime.datetime.strptime(
                event["start"]["dateTime"][:-6], "%Y-%m-%dT%H:%M:%S"
            )
            return start_date
        except:
            start_date = datetime.datetime.strptime(event["start"]["date"], "%Y-%m-%d")
            return start_date

    def turn_off_switches(self, kwargs):
        if not self.events_in_range():
            return
        if self.off_phrase:
            for speaker in self.speakers:
                self.log(TAG + " tts/google_say " + self.off_phrase)
                self.call_service(
                    "tts/google_say", entity_id=speaker, message=self.off_phrase
                )
        for switch in self.switches:
            self.turn_off(switch)
        self.log("turning off")

    def turn_on_switches(self, kwargs):
        if not self.events_in_range():
            return
        if self.on_phrase:
            for speaker in self.speakers:
                self.call_service(
                    "tts/google_say", entity_id=speaker, message=self.on_phrase
                )
        for switch in self.switches:
            self.turn_on(switch)
        self.log("turning on")