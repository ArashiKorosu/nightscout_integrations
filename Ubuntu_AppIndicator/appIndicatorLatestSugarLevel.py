#!/usr/bin/python3

# This will add a blood drop icon, last glucose reading and directional arrrow on the top panel.
# Replace ##TOKEN## with a access token of your nightscout instance (needs to have read permission)
# Replace both ##URL## with your nigthscout instance URL as example: https://example.herokuapp.com

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
gi.require_version('GLib', '2.0')
from gi.repository import Gtk, AppIndicator3, GLib
from gi.repository import AppIndicator3 as appindicator
from gi.repository import Gtk as gtk
import subprocess
import sys
import requests
import time

# Define the direction to ASCII arrow mapping
DIRECTIONS = {
    "NONE": "→",
    "DoubleUp": "⇈",
    "SingleUp": "↑",
    "FortyFiveUp": "↗",
    "Flat": "→",
    "FortyFiveDown": "↘",
    "SingleDown": "↓",
    "DoubleDown": "⇊",
    "NOT COMPUTABLE": "?",
    "RATE OUT OF RANGE": "!"
}

# Function to get the glucose readings
def get_glucose_readings():
    try:
        print("Fetching access token...")
        access_token = 'token=##TOKEN##'
        auth_url = f'##URL##/api/v2/authorization/request/{access_token}'
        auth_response = requests.get(auth_url)
        auth_response.raise_for_status()
        jwt = auth_response.json()['token']
        print("Access token fetched successfully.")
        
        print("Fetching glucose readings...")
        data_url = '##URL##/api/v3/entries?sort$desc=date&limit=3&fields=dateString,sgv,direction'
        headers = {'Authorization': f'Bearer {jwt}'}
        data_response = requests.get(data_url, headers=headers)
        data_response.raise_for_status()
        
        latest_reading = data_response.json()['result'][0]
        print("Glucose readings fetched successfully.")
        sgv = latest_reading['sgv']
        direction = latest_reading['direction']
        direction_arrow = DIRECTIONS.get(direction, "?")
        return sgv, direction_arrow
    except Exception as e:
        print(f"Error fetching glucose readings: {e}")
        return "Error", "Error"

# Function to update the indicator
def update_indicator(indicator):
    print("Updating indicator...")
    sgv, direction_arrow = get_glucose_readings()
    print(f"SGV: {sgv}, Direction: {direction_arrow}")
    indicator.set_label(f" {sgv} {direction_arrow}", "")
    return True

def exit_menu(self):
    sys.exit(0)

def menuitem_response(w, buf):
    print(buf)

if __name__ == "__main__":
    ind = appindicator.Indicator.new(
        "glucose-indicator",
        "blood",
        appindicator.IndicatorCategory.APPLICATION_STATUS
    )
    ind.set_status(appindicator.IndicatorStatus.ACTIVE)
    ind.set_icon_full("blood", "Glucose Indicator")
    
    # create a menu
    menu = Gtk.Menu()
    exit = gtk.MenuItem(label="Exit")
    exit.connect("activate", exit_menu)
    exit.show()
    menu.append(exit)
    menu.show()
    ind.set_menu(menu)

    # Update the indicator every minute
    GLib.timeout_add_seconds(60, update_indicator, ind)
    
    Gtk.main()