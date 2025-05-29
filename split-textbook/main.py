# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pymupdf",
# ]
# ///

import fitz  # PyMuPDF
import os

# File path
input_pdf_path = (
    "Monarch and Manning - Human-in-the-Loop Machine Learning Active Learnin.pdf"
)
doc = fitz.open(input_pdf_path)

# Offset because book page 1 = PDF page 27
offset = 26

# Define structure: chapters → list of (subchapter_name, book_page_number)
chapters = {
    "01_Introduction": [
        ("01.1_The_Basics", 4),
        ("01.2_Introducing_Annotation", 5),
        ("01.3_Introducing_Active_Learning", 8),
        ("01.4_HCI", 14),
        ("01.5_Assisted_HITL", 16),
        ("01.6_Transfer_Learning", 17),
        ("01.7_What_to_Expect", 21),
    ],
    "02_Getting_Started": [
        ("02.1_First_AL_Algorithm", 24),
        ("02.2_System_Architecture", 25),
        ("02.3_Model_Predictions", 29),
        ("02.4_Interface_for_Labels", 34),
        ("02.5_Deploying_HITL", 38),
    ],
    "03_Uncertainty_Sampling": [
        ("03.1_Interpreting_Uncertainty", 52),
        ("03.2_Algorithms_for_Uncertainty", 56),
        ("03.3_Model_Confusion", 65),
        ("03.4_Ensembles_and_Committee", 69),
        ("03.5_Budget_Constraints", 74),
        ("03.6_Evaluating_AL", 77),
        ("03.7_Cheat_Sheet", 79),
        ("03.8_Further_Reading", 82),
    ],
    "04_Diversity_Sampling": [
        ("04.1_Model_Knowledge_Gaps", 85),
        ("04.2_Model-Based_Outliers", 93),
        ("04.3_Cluster-Based_Sampling", 99),
        ("04.4_Representative_Sampling", 108),
        ("04.5_Real_World_Diversity", 113),
        ("04.6_Diversity_By_Model", 118),
        ("04.7_Cheat_Sheet", 119),
        ("04.8_Further_Reading", 121),
    ],
    "05_Advanced_Active_Learning": [
        ("05.1_Combining_AL_Strategies", 124),
        ("05.2_ATL_Uncertainty", 138),
        ("05.3_ATL_Representative", 144),
        ("05.4_ATL_Adaptive", 147),
        ("05.5_Cheat_Sheets", 151),
        ("05.6_Further_Reading", 154),
    ],
    "06_Applying_AL_Tasks": [
        ("06.1_Object_Detection", 157),
        ("06.2_Semantic_Segmentation", 169),
        ("06.3_Sequence_Labeling", 173),
        ("06.4_Language_Generation", 180),
        ("06.5_Other_Tasks", 183),
        ("06.6_Review_Volume", 186),
        ("06.7_Further_Reading", 188),
    ],
    # Continue adding chapters 07–12 if desired.
}


# Utility function: convert book page to PDF page
def book_to_pdf(book_page):
    return book_page + offset - 1  # 0-indexed


# Create output directory
os.makedirs("chapters", exist_ok=True)

# Loop through all chapters and their subchapters
for chapter, subchapters in chapters.items():
    chapter_dir = os.path.join("chapters", chapter)
    os.makedirs(chapter_dir, exist_ok=True)

    for i, (sub_name, start_book_page) in enumerate(subchapters):
        # Determine end page (start of next subchapter or end of doc)
        if i + 1 < len(subchapters):
            end_book_page = subchapters[i + 1][1]
        else:
            # If last subchapter, guess or slice until next chapter (or end of file)
            next_chapter_index = list(chapters.keys()).index(chapter) + 1
            if next_chapter_index < len(chapters):
                next_chapter = list(chapters.keys())[next_chapter_index]
                end_book_page = chapters[next_chapter][0][1]
            else:
                end_book_page = doc.page_count - offset + 1  # to end of doc

        start_pdf_page = book_to_pdf(start_book_page)
        end_pdf_page = book_to_pdf(end_book_page) - 1

        # Extract subchapter pages
        sub_doc = fitz.open()
        sub_doc.insert_pdf(doc, from_page=start_pdf_page, to_page=end_pdf_page)
        out_path = os.path.join(chapter_dir, f"{sub_name}.pdf")
        sub_doc.save(out_path)
        sub_doc.close()

print("✅ Finished splitting PDF into chapters and subchapters!")
