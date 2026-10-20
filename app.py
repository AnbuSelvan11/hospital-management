from flask import Flask, render_template, request, redirect
from pymongo import MongoClient
from bson.objectid import ObjectId
import re
app = Flask(__name__)

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["hospital"]

patients = db["patients"]
doctors = db["doctors"]
appointments = db["appointments"]


@app.route("/")
def home():
    return render_template(
        "index.html",
        total_patients=patients.count_documents({}),
        total_doctors=doctors.count_documents({}),
        total_appointments=appointments.count_documents({}),
    )


@app.route("/patients", methods=["GET", "POST"])
def patients_page():
    if request.method == "POST":
        patients.insert_one({
            "name": request.form["name"],
            "age": request.form["age"],
            "gender": request.form["gender"],
            "phone": request.form["phone"],
            "disease": request.form["disease"],
        })
        return redirect("/patients")
    query = request.args.get("q", "")
    if query:
        result = patients.find({"name": {"$regex": re.escape(query), "$options": "i"}})
    else:
        result = patients.find()
    return render_template("patients.html", all_patients=result)


@app.route("/patients/delete/<id>")
def delete_patient(id):
    patients.delete_one({"_id": ObjectId(id)})
    return redirect("/patients")


@app.route("/doctors", methods=["GET", "POST"])
def doctors_page():
    if request.method == "POST":
        doctors.insert_one({
            "name": request.form["name"],
            "specialization": request.form["specialization"],
            "phone": request.form["phone"],
        })
        return redirect("/doctors")
    return render_template("doctors.html", all_doctors=doctors.find())


@app.route("/doctors/delete/<id>")
def delete_doctor(id):
    doctors.delete_one({"_id": ObjectId(id)})
    return redirect("/doctors")


@app.route("/appointments", methods=["GET", "POST"])
def appointments_page():
    if request.method == "POST":
        appointments.insert_one({
            "patient": request.form["patient"],
            "doctor": request.form["doctor"],
            "date": request.form["date"],
            "reason": request.form["reason"],
        })
        return redirect("/appointments")
    return render_template(
        "appointments.html",
        all_appointments=appointments.find(),
        all_patients=patients.find(),
        all_doctors=doctors.find(),
    )


@app.route("/appointments/delete/<id>")
def delete_appointment(id):
    appointments.delete_one({"_id": ObjectId(id)})
    return redirect("/appointments")

@app.route("/patients/edit/<id>", methods=["GET", "POST"])
def edit_patient(id):
    if request.method == "POST":
        patients.update_one(
            {"_id": ObjectId(id)},
            {"$set": {
                "name": request.form["name"],
                "age": request.form["age"],
                "gender": request.form["gender"],
                "phone": request.form["phone"],
                "disease": request.form["disease"],
            }}
        )
        return redirect("/patients")
    patient = patients.find_one({"_id": ObjectId(id)})
    return render_template("edit_patient.html", p=patient)
if __name__ == "__main__":
    app.run(debug=True)