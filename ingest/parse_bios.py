import pymupdf
import json
import pandas as pd
import os

def parse_bios(users_csv="data/users.csv", resume_folder="data/resume", output_file="data/parsed_bios.jsonl"):
    users = pd.read_csv(users_csv)
    entries = []

    for _, row in users.iterrows():
        user_id = f"{row['ID']}"
        user_name = f"{row['Full Name']}"
        sources = []
        bio_parts = []

        linkedin_bio = row.get("LinkedIn Bio", "")
        if pd.notna(linkedin_bio) and linkedin_bio.strip():
            bio_parts.append(linkedin_bio.strip())
            sources.append("LinkedIn")

        resume_filename = row.get("Resume File", "").strip()
        resume_path = os.path.join(resume_folder, resume_filename)
        if os.path.exists(resume_path):
            try:
                doc = pymupdf.open(resume_path)
                text = " ".join([page.get_text() for page in doc])
                if text.strip():
                    bio_parts.append(text.strip())
                    sources.append("Resume.pdf")
            except Exception as e:
                print(f"Failed to read {resume_filename}: {e}")

        if bio_parts:
            entry = {
                "user_id": user_id,
                "user_name": user_name,
                "bio": " ".join(bio_parts),
                "sources": sources
            }
            entries.append(entry)
        
        with open(output_file, "w") as f:
            for entry in entries:
                f.write(json.dumps(entry) + "\n")

        print(f"Parsed {len(entries)} bios and saved to {output_file}")

if __name__ == "__main__":
    parse_bios()









"""
#Assuming that resume files are in users.csv
users_data = pd.read("data/users.csv")
resume_folder = "data/resume"
output_path = "parsed_bios.json1"

for _, row in users_data.iterrows():
    user_id = f"u{row['ID']}" #ex) u123
    resume_file = row.get("Resume File", "").strip()

    if not resume_file:
        print(f"No resume file listed for {user_id}")
        continue
    
    resume_path = os.path.join(resume_folder, resume_file)
    
    if not os.path.exists(resume_path):
        print(f"Resume not found: {resume_path}")
        continue
    
    #parse resume
    try:
        doc = pymupdf.open()
        text = ""
    except Exception as e:
        print(f"Failed to read {resume_path}: {e}")
        continue

    #create json entry
    entry = {
        "user_id": user_id,
        #TODO Pull from LinkedIn Bio
        #Is this also supposed to be in users.csv?
        "bio": text.strip(),
        "sources": [resume_file]
    }

    with open(output_path, "a") as f:
        f.write(json.dumps(entry) + "\n")
    
    print(f"Parsed pdf and saved bio for {user_id}") #Again, bio not implemented


def parse_bios(pdf_path: str, user_id: str, output_filepath: str="parsed_bios.jsonl"):
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at {pdf_path}")
        return
    try:
        bio_text = ""
        with pymupdf.open(pdf_path) as doc:
            for page_num in range(doc.page_count):
                page = doc.load_page(page_num)
                bio_text += page.get_text()
        bio_text = ' '.join(bio_text.split()).strip()

        data = {
            "user_id": user_id,
            "bio": bio_text,
            "sources": ["Resume.pdf"] #Assuming the PDF is the primary source
        }

        with open(output_filepath, 'a', encoding='utf-8') as f:
            f.write(json.dumps(data, ensure_ascii=False) + '\n')
        print(f"Successfully parsed {pdf_path} for user {user_id} and saved to {output_filepath}")
    except Exception as e:
        print(f"An error occurred while processing {pdf_path}: {e}")
"""
