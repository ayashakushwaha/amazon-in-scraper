import sys
import csv

import requests
from bs4 import BeautifulSoup

def cleanText(text):
    return text.strip().replace("\u200e", "").replace("\n", "").replace('  ', "")

f = open('product_details.csv', 'w', encoding="utf-8", newline='')
writer = csv.writer(f)

sys.stdin.reconfigure(encoding='utf-8')
sys.stdout.reconfigure(encoding='utf-8')

writer.writerow(["product_name", "product_url", "product_price", "rating", "num_of_reviews", "description", "asin", "product_description", "manufacturer"])
base_url="https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_1"
headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }

product_count=0
for i in range(20):
    if product_count >=200:
        break
    
    # get product listings
    url=f"{base_url}&page={i+1}"
    r=requests.get(url, headers=headers)
    soup=BeautifulSoup(r.content,"html.parser")
    product_list=soup.find_all("div",class_="s-card-container")
    
    for product in product_list:
        try:     
            product_name=product.find("h2").text
            product_url=product.find("a", class_="a-text-normal").get("href")
            if not product_url.startswith("https://"):
                product_url="https://www.amazon.in"+product_url
                
            product_price=product.find("span", class_="a-price-whole").text
            
            rating=""
            num_reviews=""
            if product.find("span", class_="a-icon-alt"):
                rating=product.find("span", class_="a-icon-alt").text
                num_reviews=product.find("span", class_="a-size-base").text
            
            # call product item page to extract additional info
            try:
                req=requests.get(product_url, headers=headers)
                soup1=BeautifulSoup(req.content,"html.parser")
            except Exception as e:
                continue
            
            description=soup1.find("div",id="feature-bullets").text
            
            # product descrption can be in multiple div
            product_description_div=soup1.find("div", class_="aplus-v2")
            if not product_description_div:
                product_description_div=soup1.find("div", id="productDescription")
            
            product_description=product_description_div.text
            
            asin=""
            manufacturer=""    
            product_details=soup1.find("div",id="detailBullets_feature_div")
            technical_info_table=soup1.find("table",id="productDetails_techSpec_section_1")
            additional_info_table=soup1.find("table",id="productDetails_detailBullets_sections1")
            
            # find ASIN and Manufacturer in product details
            if product_details:
                details_list=product_details.find_all("li")
                for li in details_list:
                    li_text_cleaned=li.text.strip().replace("  ", "").replace("\n", "")
                    if not asin and li_text_cleaned.startswith("ASIN"):
                        asin=li_text_cleaned.split(":")[1].strip()
                    elif not manufacturer and li_text_cleaned.startswith("Manufacturer"): 
                        manufacturer = li_text_cleaned.split(":")[1].strip()
            
            # find ASIN and Manufacturer in technical_info_table
            if (not manufacturer or not asin) and technical_info_table:
                for row in technical_info_table.find_all("tr"):
                    cleaned_row=row.text.strip()
                    if not asin and cleaned_row.startswith("ASIN"):
                        asin = cleaned_row.split("   ")[1]
                    elif not manufacturer and cleaned_row.startswith("Manufacturer"):
                        manufacturer = cleaned_row.split("   ")[1]
            
            # find ASIN and Manufacturer in product additional_info_table
            if (not manufacturer or not asin) and additional_info_table:
                for row in additional_info_table.find_all("tr"):
                    cleaned_row=row.text.strip()
                    if not asin and cleaned_row.startswith("ASIN"):
                        asin = cleaned_row.split("   ")[1]
                    elif not manufacturer and cleaned_row.startswith("Manufacturer"):
                        manufacturer = cleaned_row.split("   ")[1]
                    
            # write product details into csv file
            writer.writerow([cleanText(data) for data in [product_name, product_url, product_price, rating, num_reviews, description, asin, product_description, manufacturer]])
            product_count+=1
        except Exception as e:
            continue
f.close()             