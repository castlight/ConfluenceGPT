from atlassian import Confluence
from dotenv import load_dotenv
import os
from src.config.appconfiguration import getAreaToRootPages
from cryptography.fernet import Fernet
import numpy as np


load_dotenv()

url=os.environ.get('CONFLUENCE_URL')
username=os.environ.get('CONFLUENCE_USERNAME')
encrypted_api_key=os.environ.get('CONFLUENCE_PASSWORD_OR_APIKEY')
key = os.environ.get('CONFLUENCE_APIKEY_ENCKEY')
f = Fernet(key)
api_key=f.decrypt(encrypted_api_key)

ALL_PAGES='All'

confluence = Confluence(url, username, api_key)


def getArea():
    area=[]
    area.append(ALL_PAGES)
    for mapping in getAreaToRootPages():
        area.append(mapping[0])
    return area
def get_children_page_ids(parent_page_ids):
    from src.config.appconfiguration import getExcludedPages
    children_page_ids = []
    for parent_page_id in parent_page_ids:
        children = confluence.get_child_id_list(page_id=parent_page_id)
        children_page_ids.extend(children)
        #2nd level
        for childid in children:
            if childid not in getExcludedPages():
                grandchildren = confluence.get_child_id_list(page_id=childid)
                children_page_ids.extend(grandchildren)
            #3rd level
            for gchild in grandchildren:
                if gchild not in getExcludedPages():
                    grandgrandchildren = confluence.get_child_id_list(page_id=gchild)
                    children_page_ids.extend(grandgrandchildren)

    return children_page_ids


all_children_page_ids = []


def getAllPageIds():
    print("len(all_children_page_ids): ",len(all_children_page_ids))
    if(len(all_children_page_ids) > 0):
        return all_children_page_ids

    totalPages=0
    all_pages=[]
    for mapping in getAreaToRootPages():
        area=mapping[0]
        pages=mapping[1]
        print('Area: ',area)
        print('Pages: ',pages)
        children_ids = get_children_page_ids(pages)
        children_ids.extend(list(map(str, pages))) #Add root page, after convertin ids to string
        children_ids=np.unique(children_ids).tolist()
        all_pages.extend(children_ids)
        totalPages += len(children_ids)
        print('child pages for area', area)
        print(children_ids)
        print('total number of pages for area: '+str(area)+': '+str(len(children_ids)))
        entry={'area': area, 'pages': children_ids}
        all_children_page_ids.append(entry)
        print('============================================================================')

    #Support for All Pages
    all_pages=np.unique(all_pages).tolist()
    all_entry={'area': ALL_PAGES, 'pages': all_pages}
    all_children_page_ids.append(all_entry)

    print('=================== Total no of pages: =============== '+ str(totalPages)+ ', length of all_pages: '+str(len(all_pages)))
    print(all_children_page_ids)
    return all_children_page_ids




#if __name__ == "__main__":
 #   print("Calling getAllPageIds")
  #  getAllPageIds()