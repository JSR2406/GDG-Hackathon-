from app.database import SessionLocal
from app import crud, schemas

def seed_demo_data():
    """Seed database with demo data for perfect 3-way cycle"""
    db = SessionLocal()
    
    try:
        print("🌱 Seeding demo data...")
        
        # Create 3 users
        print("\n👥 Creating users...")
        arun = crud.create_user(db, schemas.UserCreate(
            name="Arun Kumar",
            email="arun@campus.edu",
            semester=5,
            department="Mechanical Engineering",
            hostel="Hostel A"
        ))
        print(f"✅ Created user: {arun.name} (ID: {arun.id})")
        
        priya = crud.create_user(db, schemas.UserCreate(
            name="Priya Sharma",
            email="priya@campus.edu",
            semester=5,
            department="Mechanical Engineering",
            hostel="Hostel B"
        ))
        print(f"✅ Created user: {priya.name} (ID: {priya.id})")
        
        ravi = crud.create_user(db, schemas.UserCreate(
            name="Ravi Patel",
            email="ravi@campus.edu",
            semester=6,
            department="Computer Science",
            hostel="Hostel A"
        ))
        print(f"✅ Created user: {ravi.name} (ID: {ravi.id})")
        
        # Create 3 items
        print("\n📦 Creating items...")
        drafter = crud.create_item(db, schemas.ItemCreate(
            name="Professional Drafting Compass Set",
            category="drafting tools",
            condition="good",
            department="Mechanical Engineering"
        ), arun.id)
        print(f"✅ Created item: {drafter.name} (ID: {drafter.id}) - Owner: Arun")
        
        textbook = crud.create_item(db, schemas.ItemCreate(
            name="Engineering Mechanics Textbook",
            category="textbook",
            condition="excellent",
            department="Mechanical Engineering"
        ), priya.id)
        print(f"✅ Created item: {textbook.name} (ID: {textbook.id}) - Owner: Priya")
        
        lab_coat = crud.create_item(db, schemas.ItemCreate(
            name="Laboratory Safety Coat",
            category="lab equipment",
            condition="good",
            department="Chemistry"
        ), ravi.id)
        print(f"✅ Created item: {lab_coat.name} (ID: {lab_coat.id}) - Owner: Ravi")
        
        # Create 3 barter edges forming perfect cycle
        print("\n🔄 Creating barter intents (forming 3-way cycle)...")
        
        # Arun has Drafter → wants Textbook
        edge1 = crud.create_barter_edge(db, schemas.BarterIntentCreate(
            item_id=drafter.id,
            want_category="textbook",
            want_description="Engineering textbook for mechanics course",
            emergency=False
        ), arun.id)
        print(f"✅ Arun wants: Textbook (has Drafter)")
        
        # Priya has Textbook → wants Lab Coat
        edge2 = crud.create_barter_edge(db, schemas.BarterIntentCreate(
            item_id=textbook.id,
            want_category="lab equipment",
            want_description="Lab coat for chemistry practicals",
            emergency=False
        ), priya.id)
        print(f"✅ Priya wants: Lab Equipment (has Textbook)")
        
        # Ravi has Lab Coat → wants Drafter
        edge3 = crud.create_barter_edge(db, schemas.BarterIntentCreate(
            item_id=lab_coat.id,
            want_category="drafting tools",
            want_description="Drafting tools for engineering drawing",
            emergency=False
        ), ravi.id)
        print(f"✅ Ravi wants: Drafting Tools (has Lab Coat)")
        
        print("\n🎯 Perfect 3-way cycle created!")
        print("   Arun (Drafter) → Priya (Textbook) → Ravi (Lab Coat) → Arun")
        print("\n✨ Demo data seeded successfully!")
        print("\n📝 Next steps:")
        print("   1. Start the backend: python uvicorn_run.py")
        print("   2. Visit http://localhost:8000/docs")
        print("   3. Test the matching by calling POST /api/v1/barter-intents")
        
    except Exception as e:
        print(f"❌ Error seeding data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_demo_data()
