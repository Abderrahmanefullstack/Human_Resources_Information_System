# Human Resources Information System (HRIS)

A modern **Human Resources Information System (HRIS)** built with **Django** and connected to **SQL Server**.  
The platform centralizes employee data, manages functions, entities, and internal announcements, while also supporting ** Excel imports/exports** and the **automatic generation of official HR documents** (assignment letters, commission reports, etc.).  
The interface is styled with **Bootstrap 5**, providing a professional, responsive, and user-friendly design.

---

## 🚀 Features

- **Excel Import & Export**  
  - Intelligent column cleaning & mapping (with `pandas`, `unidecode`)  
  - Automatic replacement of old data during import  
  - Export clean and structured HR reports  

- **Employee (Agent) Management**  
  - Database with 180+ fields  
  - Interface focused on 10 key fields for simplicity  
  - Advanced search & filters (matricule, name, gender, retirement year)  

- **Functions & Entities**  
  - CRUD operations for job functions and organizational entities  
  - Entities auto-created during agent import (no duplication)  

- **Document Generation**  
  - Automated **assignment letters** (*lettres d’affectation*)  
  - Automated **commission reports** (*procès-verbaux des commissions*)  
  - Export in **PDF** and **Word** format with official styling  

- **Internal Announcements**  
  - HR can create, edit, and delete announcements  
  - Announcement list with filters for internal communication  

- **User Interface**  
  - Built with **Bootstrap 5** + **Font Awesome**  
  - Sidebar and theme inspired by corporate branding (banking sector)  
  - Responsive, modern, and HR-focused  

---

## 🛠️ Tech Stack

- **Backend:** Django (Python)  
- **Database:** SQL Server (MS SQL)  
- **Frontend:** Bootstrap 5, HTML, CSS, JavaScript  

**Libraries & Tools**  
- Data processing: `pandas`, `unidecode`, `tqdm`  
- Excel handling: `openpyxl`  
- PDF generation: `reportlab`  
- Word/Office: `python-docx`, `python-pptx`, `openpyxl`, `odfpy`  
- File conversion: `pypandoc`  

---

## 📂 Project Structure

- `agents/` → Manage employee records  
- `fonctions/` → Manage job functions  
- `entites/` → Manage entities/organizational structure  
- `annonces/` → Manage internal announcements  
- `users/` → Authentication & user management  
- `templates/` → Bootstrap-based HTML templates  
- `static/` → Static files (CSS, JS, images)  

---
