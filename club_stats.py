""" Program to get the statistics from the members of a Chess Club
    in chess.com using the API for public data defined in:
    https://www.chess.com/news/view/published-data-api
    Change CLUB_NAME to the name of the corresponding club
    Output data is written to Club_Data.xlsx spreadsheet
    Generates and optional Ratings Chart on screen

    Author: Fernando Agostino
    Version 1.1
"""

import json
from urllib.request import urlopen
from pandas import DataFrame
from matplotlib import pyplot as plt

# Club name as indicated in the last part of the Club's URL
CLUB_NAME = "mensa-argentina"
# Set to False if not rating chart is desired on screen
PLOT = True

# Print progress message
print("Getting list of club members from web site...")

# Get JSON response with club members data
try:
    with urlopen(
        "https://api.chess.com/pub/club/" + CLUB_NAME + "/members"
    ) as response:
        source = response.read()
except:
    print("Error: Unable to access web site")
    exit(1)

# Convert JSON to a Python dict
club_members = json.loads(source)

# Initialize empty list for members user names
members = list()

# Create the list of all the club members
# There are three different keys (weekly, annual, all-time) grouping the list of members
# Not interested in that grouping so read the values of each one
for type_list in club_members.values():
    # For each member in that list, append only the user name to the list of members
    for element in type_list:
        # Create temporary empty dictionary to gather new member info
        new_member = {}
        # Read and record username
        new_member["username"] = element["username"]
        # Add new member to the list of members
        members.append(new_member)

# Sort the list of members alphabetically by 'username'
members.sort(key=lambda i: i["username"])

# Print club name and number of club members
print("Club Name: ", CLUB_NAME)
print("Number of Club members: ", len(members))

# Print progress message
print("Getting Players information from web site...")

# Gather additional profile information for each club member
for member in members:
    # Get JSON response with member's data
    try:
        with urlopen(
            "https://api.chess.com/pub/player/" + member["username"]
        ) as response:
            source = response.read()
    except:
        print("Error: Unable to access web site")
        exit(1)
    # Convert JSON response with player's data into Python dict
    player_data = json.loads(source)
    # Read and record member's name (or empty string if not available)
    member["name"] = player_data["name"] if "name" in player_data else ""
    # Read and record member's location (or empty string if not available)
    member["location"] = player_data["location"] if "location" in player_data else ""
    # Read and record member's status (or empty string if not available)
    member["status"] = player_data["status"] if "status" in player_data else ""

# Define list of rating types to include in the ratings table
rating_lists = {
    "chess_daily": "last",
    "chess_rapid": "last",
    "chess_blitz": "last",
    "chess_bullet": "last",
    "chess960_daily": "last",
    "tactics": "highest",
    "lessons": "highest",
}

# Print progress message
print("Getting Stats information from web site...")

# Read stats for each club member
for member in members:
    # # Get JSON response with member's stats
    try:
        with urlopen(
            "https://api.chess.com/pub/player/" + member["username"] + "/stats"
        ) as response:
            source = response.read()
    except:
        print("Error: Unable to access web site")
        exit(1)
    # Convert JSON response into a Python dictionary
    player_data = json.loads(source)

    # Read and record member's FIDE ELO (or empty string if not available or is zero)
    member["fide"] = player_data["fide"] if "fide" in player_data else ""
    if member["fide"] == 0:
        member["fide"] = ""

    # Read Puzzle Rush Score
    try:
        # If key exists, copy its value as an integer
        member["puzzle_rush"] = player_data["puzzle_rush"]["best"]["score"]
    except KeyError:
        # Key does not exists. Store empty string
        member["puzzle_rush"] = ""

    # Read rating for each type of game
    for rating_type in rating_lists:
        try:
            # If key exists, copy its value as an integer
            member[rating_type] = player_data[rating_type][rating_lists[rating_type]][
                "rating"
            ]
        except KeyError:
            # Key does not exists. Store empty string
            member[rating_type] = ""

print("Writing output file")
# Create a pandas DataFrame with the list of members and their data
df = DataFrame(members)
# Write all the information to an Excel spreadsheet
df.to_excel(
    "Club_Data.xlsx",
    sheet_name="Club Data",
    index=False,
    freeze_panes=(1, 1),
    columns=[
        "username",
        "name",
        "fide",
        "chess_daily",
        "chess_rapid",
        "chess_blitz",
        "chess_bullet",
        "chess960_daily",
        "tactics",
        "lessons",
        "puzzle_rush",
        "location",
        "status",
    ],
    header=[
        "Username",
        "Name",
        "FIDE",
        "Daily",
        "Rapid",
        "Blitz",
        "Bullet",
        "960 Daily",
        "Tactics",
        "Lessons",
        "Puzzle",
        "Location",
        "Status",
    ],
)

# Exit program if ratings chart is not desired
if PLOT == False:
    exit(0)

# Prepare the data for plotting
print("Drawing chart...")

rating_types = [
    "chess_daily",
    "chess_rapid",
    "chess_blitz",
    "chess_bullet",
    "chess960_daily",
    "tactics",
]

rating_names = ["Daily", "Rapid", "Blitz", "Bullet", "Daily 960", "Tactics"]

# Create an empty dictionary that will have the username and the ratings for each player
ratings = {}

# Set style of chart
plt.style.use("seaborn-dark")

# Fill in the lists of each rating type for every player
for member in members:
    # Get the user ID
    uid = member["username"]
    # Initialize the rating list for that player to empty string
    ratings[uid] = list()
    for type in rating_types:
        # For each rating type, append the rating to the user's list
        ratings[uid].append(int(member[type]) if member[type] != "" else 800)

# Plot each line
for member in members:
    uid = member["username"]
    plt.plot(rating_names, ratings[uid], label=uid)

# Set chart labels, axis names and titles
plt.xlabel("Game Type")
plt.ylabel("ELO")
plt.legend()
plt.title("Ranking of Players of Club " + CLUB_NAME)
# Show the chart
plt.show()
