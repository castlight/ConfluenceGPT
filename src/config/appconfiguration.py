import os
from flask import jsonify
#Use this page to configure below :
# logos and icons shown on the internal chatGPT screen,
# the confluence pages to be used for your use case.


# Change logos and icons here - Keep the names of your logos same as in the path mentioned in below method But
# either replace existing logos with your ones
# OR change the path to a new folder where you are keeping logos(with same logo names)
def getLogosFolder():
    return os.path.abspath('./src/static')


# Configure the text for the page as per your Company/ Organisation here
def getPageText():
    companyName = 'MyCompany';
    title = companyName+'GPT';
    appName = companyName+"GPT";
    appDescription = "Ask questions on "+companyName+" domain."
    chooseAreatext = "Choose an area to ask question from :"
    text = "Note: This is a private LLM and all data stays local to the company. You can ask it questions about a subset of the data in our Confluence wiki. It shall respond with an answer using the data from possibly one/more relevant confluence pages.";
    exampleQuestion1Area="Area: Project1"           #Refer to the exact key name in 'area_to_root_page_id' below
    exampleQuestion1="Question: Please summarise the 'Project1'."
    exampleQuestion2Area="Area: Architectures"      #Refer to the exact key name in 'area_to_root_page_id' below
    exampleQuestion2="Question: Please provide architecture details of how data flows in project 'x'."
    exampleQuestion3Area="Area: Process"            #Refer to the exact key name in 'area_to_root_page_id' below
    exampleQuestion3="Question: What is the process to get access to the source code."
    exampleQuestion4Area="Area: Onboarding"        #Refer to the exact key name in 'area_to_root_page_id' below
    exampleQuestion4="Question: Please help me with the links for onboarding process for a new company"

    return {"title": title, "appName": appName, "appDescription": appDescription, "chooseAreatext":chooseAreatext, "text": text, "exampleQuestion1Area": exampleQuestion1Area, "exampleQuestion1": exampleQuestion1,
            "exampleQuestion2Area":exampleQuestion2Area, "exampleQuestion2":exampleQuestion2, "exampleQuestion3Area":exampleQuestion3Area,
            "exampleQuestion3":exampleQuestion3, "exampleQuestion4Area":exampleQuestion4Area, "exampleQuestion4":exampleQuestion4}


#Confluence Page Configuration
# Entry Format - "<Display Name Of The Area>":[comma separated list of root confluence page IDs]
# The key is displayed on the UI in the drop-down. User can select the area to ask questions from the pages mapped to this area in below dictionary.
# Dividing your confluence space into area result in providing lot more accurate results for questions because the app looks out for data within the index
# created from these pages.
area_to_root_page_id=[
    ['Project1', ['<confluence_page_id_for_root_page_for_Project1>', '<another_confluence_page_id_for_root_page_for_Project1>']],
    ['Project2', ['<confluence_page_id_for_root_page_for_Project2>', '<another_confluence_page_id_for_root_page_for_Project2>']],
    ['Department1', ['<confluence_page_id_for_root_page_for_Department1>']],
    ['Department2', ['<confluence_page_id_for_root_page_for_Department2>']],
    ['Team1', ['<confluence_page_id_for_root_page_for_Team1>']],
    ['Team2', ['<confluence_page_id_for_root_page_for_Team2>']],
    ['Retrospectives', ['<confluence_page_id_for_root_page_for_retrospectives_of_Team1>','<confluence_page_id_for_root_page_for_retrospectives_of_Team2>']],
    ['Onboarding', ['<confluence_page_id_for_root_page_for_new_member_onboarding>']],
    ['Architectures', ['<confluence_page_id_for_root_page_for_architecture_docs>']],
    ['Process', ['<confluence_page_id_for_root_page_for_different_processes>']]
]


# Exclude any page so that this page as well as its children will be excluded while answering a question
#There may be many pages in confluence which migth be obsolete OR irrelevant for your use case but are child of some page mentioned in 'area_to_root_page_id'.
exclude_list_ids = ['<confluence_page_id1>', '<confluence_page_id2>']

def getExcludedPages():
    return exclude_list_ids

def getAreaToRootPages():
    return area_to_root_page_id


