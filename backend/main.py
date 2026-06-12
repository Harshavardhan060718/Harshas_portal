from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List

# Import firebase client instance
from backend.firebase_config import db
from backend.schemas import RecordCreate, RecordResponse

app = FastAPI(
    title="AegisPortal Firestore API",
    description="Backend API connected to Firebase Firestore for managing database staff records",
    version="1.0.0"
)

# Enable CORS for frontend applications loaded from local files or other domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permits all origins (including file://)
    allow_credentials=True,
    allow_methods=["*"],  # Permits all standard methods (GET, POST, DELETE, etc.)
    allow_headers=["*"],  # Permits all request headers
)

# Seed initial Firestore database records if collection is completely empty
@app.on_event("startup")
def seed_database():
    try:
        records_ref = db.collection("records")
        # Check if any documents exist in the collection
        docs = list(records_ref.limit(1).stream())
        if len(docs) == 0:
            mock_records = [
                {
                    "full_name": "Alexander Pierce",
                    "email": "alexander.p@company.com",
                    "job_title": "Lead DevOps Architect",
                    "department": "Engineering",
                    "salary": 142000,
                    "status": "Active",
                    "notes": "Oversees containerization, Kubernetes clusters, and automated deployment pipelines."
                },
                {
                    "full_name": "Jane Foster",
                    "email": "jane.foster@company.com",
                    "job_title": "Senior UI/UX Designer",
                    "department": "Design",
                    "salary": 115000,
                    "status": "Active",
                    "notes": "Leads visual system guidelines, typography scales, and interactive user experience journeys."
                },
                {
                    "full_name": "Marcus Vance",
                    "email": "m.vance@company.com",
                    "job_title": "Product Director",
                    "department": "Product",
                    "salary": 155000,
                    "status": "Pending",
                    "notes": "Focuses on strategic product roadmaps, cross-team synergy, and high-impact quarterly goals."
                },
                {
                    "full_name": "Sophia Martinez",
                    "email": "s.martinez@company.com",
                    "job_title": "Marketing Executive",
                    "department": "Marketing",
                    "salary": 89000,
                    "status": "Suspended",
                    "notes": "Manages digital outreach, performance advertising campaigns, and media relations."
                }
            ]
            
            # Batch write for atomicity and efficiency
            batch = db.batch()
            for record in mock_records:
                doc_ref = records_ref.document()
                batch.set(doc_ref, record)
            batch.commit()
            print("[INFO] Cloud Firestore successfully seeded with default records.")
    except Exception as e:
        print(f"[WARNING] Database seeding failed or credentials not fully ready: {e}")

# API Endpoints

@app.get("/api/records", response_model=List[RecordResponse])
def get_records():
    """Fetch all staff records from Google Cloud Firestore."""
    try:
        records_ref = db.collection("records")
        docs = records_ref.stream()
        records_list = []
        for doc in docs:
            data = doc.to_dict()
            data["id"] = doc.id  # Firestore document ID string
            records_list.append(data)
        return records_list
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database query failed: {str(e)}"
        )

@app.post("/api/records", response_model=RecordResponse, status_code=status.HTTP_201_CREATED)
def create_record(record_in: RecordCreate):
    """Create a new staff record in Cloud Firestore."""
    try:
        records_ref = db.collection("records")
        
        # Check if email already exists in Firestore
        query = list(records_ref.where("email", "==", record_in.email).limit(1).stream())
        if len(query) > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A record with this email address already exists."
            )
        
        # Insert document and let Firestore auto-generate ID
        new_doc_ref = records_ref.document()
        data = record_in.dict()
        new_doc_ref.set(data)
        
        # Attach the generated ID to response
        data["id"] = new_doc_ref.id
        return data
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database insertion failed: {str(e)}"
        )

@app.delete("/api/records/{record_id}", status_code=status.HTTP_200_OK)
def delete_record(record_id: str):
    """Remove a staff record from Cloud Firestore by document ID string."""
    try:
        doc_ref = db.collection("records").document(record_id)
        doc = doc_ref.get()
        if not doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The specified record could not be found."
            )
        doc_ref.delete()
        return {"message": f"Record {record_id} successfully deleted."}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database deletion failed: {str(e)}"
        )
