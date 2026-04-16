import joblib
import random
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

CATEGORIES = {
    "infrastructure": [
        "The lab chair is broken and dangerous",
        "Power socket is sparking in lab",
        "Water leak in hostel bathroom",
        "Lighting not working in corridor",
        "Door lock broken in lab"
    ],
    "academic": [
        "Request extension for assignment due to illness",
        "Project group needs clarification on requirements",
        "Exam schedule clash between subjects",
        "Instructor didn't upload lecture notes"
    ],
    "hostel": [
        "Food quality in mess is bad",
        "Room fan not working",
        "Roommate creating noise at night",
        "Hot water not available in bathroom"
    ],
    "transport": [
        "College bus did not stop at my stop",
        "Driver driving recklessly on service bus",
        "Bus timing changed without notice"
    ],
    "network": [
        "WiFi not working in block A",
        "Cannot access online portal",
        "Network very slow during peak hours"
    ],
    "other": [
        "Request for new sports equipment",
        "Suggestion: more charging points",
        "Can we have a helpdesk for software issues?"
    ]
}

texts, labels = [], []
for cat, templates in CATEGORIES.items():
    for t in templates:
        for _ in range(40):
            suffix = ""
            if random.random() < 0.35:
                suffix = " " + random.choice(["please fix", "ASAP", "today", "urgent", "soon"])
            texts.append((t+suffix).strip())
            labels.append(cat)
    
combined = list(zip(texts, labels))
random.shuffle(combined)
texts, labels = zip(*combined)

X_train, X_test, Y_train, Y_test = train_test_split(list(texts), list(labels), test_size=0.15, random_state=42)

pipe = make_pipeline(
    TfidfVectorizer(ngram_range=(1,2), max_features=5000),
    LogisticRegression(max_iter=1000)
)

print("Training classifier..")
pipe.fit(X_train, Y_train)

print("Evaluating on test set:")
preds = pipe.predict(X_test)
print(classification_report(Y_test, preds))

joblib.dump(pipe, "category_pipe.pkl")
print("Saved pipeline to category_pipe.pkl")

sample_texts = [
    "Power socket is sparking in lab, very dangerous",
    "Can't access the portal to submit assignment",
    "Food served in mess is rotten"
]

print("Sample predictions: ")
for s in sample_texts:
    pred = pipe.predict([s])[0]
    prob = pipe.predict_proba([s])[0].max()
    print(f"Text: {s}\n -> Pred: {pred} (conf: {prob:.2f})\n")