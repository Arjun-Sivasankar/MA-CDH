"""
Script to set up sample medical guidelines and literature database
Run this once to populate the data directory
"""

import json
import os
from pathlib import Path


def create_guidelines_database():
    """Create sample medical guidelines database"""
    
    base_path = Path("data/guidelines")
    
    # Cardiology Guidelines
    cardiology_guidelines = {
        "aha-acc-2024-htn": {
            "id": "aha-acc-2024-htn",
            "title": "2024 AHA/ACC Guideline for the Management of High Blood Pressure in Adults",
            "organization": "American Heart Association / American College of Cardiology",
            "year": 2024,
            "sections": {
                "diagnosis": {
                    "content": "HTN is defined as BP ≥130/80 mmHg. Confirm with multiple readings over time or ambulatory BP monitoring.",
                    "key_points": [
                        "Stage 1 HTN: 130-139/80-89 mmHg",
                        "Stage 2 HTN: ≥140/90 mmHg",
                        "Use home BP monitoring for confirmation"
                    ]
                },
                "treatment": {
                    "content": "First-line therapy for HTN includes ACE inhibitors, ARBs, CCBs, or thiazide diuretics. Choice depends on comorbidities.",
                    "key_points": [
                        "ACE-I/ARB: First-line for HTN with diabetes, CKD, or proteinuria",
                        "CCB: Alternative first-line, good for elderly and African Americans",
                        "Thiazide diuretics: Effective first-line monotherapy",
                        "Beta-blockers: Second-line unless specific indication (CAD, HF)"
                    ],
                    "special_populations": {
                        "diabetes": "ACE-I or ARB preferred. Target BP <130/80 mmHg",
                        "ckd": "ACE-I or ARB if proteinuria present. Monitor K+ and Cr",
                        "elderly": "Consider lower starting doses. CCB often well-tolerated"
                    }
                },
                "monitoring": {
                    "content": "Monitor BP response, adherence, and adverse effects. Adjust therapy as needed.",
                    "key_points": [
                        "Recheck BP in 1 month after initiation",
                        "Monitor renal function and electrolytes with ACE-I/ARB",
                        "Assess for orthostatic hypotension in elderly"
                    ]
                },
                "drug-dosing": {
                    "content": "Start at standard doses unless specific contraindications. Titrate to achieve target BP.",
                    "examples": {
                        "lisinopril": "Start 10mg daily, max 40mg daily. Reduce dose if eGFR <30",
                        "amlodipine": "Start 5mg daily, max 10mg daily. No renal adjustment needed",
                        "hydrochlorothiazide": "Start 12.5-25mg daily, max 50mg daily"
                    }
                }
            },
            "references": ["PMID: 12345678", "DOI: 10.1161/CIR.2024"]
        },
        "esc-2024-heart-failure": {
            "id": "esc-2024-heart-failure",
            "title": "2024 ESC Guidelines for Heart Failure Management",
            "organization": "European Society of Cardiology",
            "year": 2024,
            "sections": {
                "treatment": {
                    "content": "Guideline-directed medical therapy (GDMT) for HFrEF includes ACE-I/ARB/ARNI, beta-blockers, MRAs, and SGLT2 inhibitors.",
                    "key_points": [
                        "Quadruple therapy is standard: ACE-I/ARB/ARNI + BB + MRA + SGLT2i",
                        "Start SGLT2i early in all HFrEF patients",
                        "Titrate to target or maximally tolerated doses"
                    ]
                }
            }
        },
        "acc-aha-2023-cholesterol": {
            "id": "acc-aha-2023-cholesterol",
            "title": "2023 ACC/AHA Guideline for Management of Blood Cholesterol",
            "organization": "ACC/AHA",
            "year": 2023,
            "sections": {
                "treatment": {
                    "content": "Statin therapy is primary prevention for ASCVD. Intensity based on risk.",
                    "key_points": [
                        "High-intensity statin for ASCVD or diabetes with risk factors",
                        "Moderate-intensity for primary prevention with 10-year risk >7.5%",
                        "Consider PCSK9 inhibitors if LDL goals not met on statin"
                    ]
                }
            }
        }
    }
    
    # Diabetes Guidelines
    diabetes_guidelines = {
        "ada-2024-standards": {
            "id": "ada-2024-standards",
            "title": "2024 ADA Standards of Medical Care in Diabetes",
            "organization": "American Diabetes Association",
            "year": 2024,
            "sections": {
                "diagnosis": {
                    "content": "Diabetes diagnosis: A1c ≥6.5%, FPG ≥126 mg/dL, or 2-hour PG ≥200 mg/dL during OGTT.",
                    "key_points": [
                        "Prediabetes: A1c 5.7-6.4%",
                        "Screen annually if risk factors present"
                    ]
                },
                "treatment": {
                    "content": "Metformin is first-line unless contraindicated. Add agents based on comorbidities and patient factors.",
                    "key_points": [
                        "Metformin: First-line, start 500mg and titrate to 2000mg daily",
                        "GLP-1 RA: Add if ASCVD, HF, or CKD present - proven CV benefit",
                        "SGLT2i: Add if HF or CKD - proven renal and cardiac protection",
                        "DPP-4i: Alternative if GLP-1/SGLT2i not tolerated",
                        "Insulin: Add if A1c >10% or significant hyperglycemia symptoms"
                    ],
                    "special_populations": {
                        "ckd": "Avoid metformin if eGFR <30. Prefer GLP-1 RA or SGLT2i for renal protection",
                        "cvd": "GLP-1 RA with proven CV benefit (liraglutide, semaglutide, dulaglutide)",
                        "heart_failure": "SGLT2i preferred (empagliflozin, dapagliflozin)"
                    }
                },
                "monitoring": {
                    "content": "Monitor A1c every 3 months until target achieved, then every 6 months.",
                    "key_points": [
                        "Target A1c <7% for most adults",
                        "Individualize: <6.5% if safe, <8% if elderly/comorbidities",
                        "Screen for complications annually"
                    ]
                },
                "drug-dosing": {
                    "examples": {
                        "metformin": "Start 500mg daily with dinner, increase by 500mg weekly. Max 2000mg daily. Take with food.",
                        "semaglutide": "Start 0.25mg SC weekly x 4 weeks, then 0.5mg weekly. Titrate to 1mg if needed.",
                        "empagliflozin": "Start 10mg daily, increase to 25mg if tolerated. Monitor for genital infections."
                    }
                }
            },
            "references": ["Diabetes Care 2024;47(Suppl 1)", "PMID: 23456789"]
        },
        "kdigo-2024-ckd-diabetes": {
            "id": "kdigo-2024-ckd-diabetes",
            "title": "KDIGO 2024 Clinical Practice Guideline for Diabetes in CKD",
            "organization": "Kidney Disease: Improving Global Outcomes",
            "year": 2024,
            "sections": {
                "treatment": {
                    "content": "Glucose-lowering therapy in CKD should prioritize renal and cardiovascular protection.",
                    "key_points": [
                        "Metformin safe until eGFR <30, then discontinue",
                        "SGLT2i: Continue until eGFR <20 for renal protection",
                        "GLP-1 RA: Safe and effective across all CKD stages",
                        "Avoid sulfonylureas in advanced CKD (hypoglycemia risk)"
                    ]
                }
            }
        }
    }
    
    # Hypertension Guidelines
    hypertension_guidelines = {
        "jnc8-htn-management": {
            "id": "jnc8-htn-management",
            "title": "JNC 8 Guidelines for Management of High Blood Pressure",
            "organization": "Joint National Committee",
            "year": 2014,
            "sections": {
                "treatment": {
                    "content": "Evidence-based recommendations for BP management in adults.",
                    "key_points": [
                        "General population <60 years: Treat if BP ≥140/90",
                        "General population ≥60 years: Treat if BP ≥150/90",
                        "Diabetes or CKD: Treat if BP ≥140/90",
                        "African Americans: Thiazide or CCB preferred initial therapy"
                    ]
                }
            }
        },
        "esc-esh-2023-htn": {
            "id": "esc-esh-2023-htn",
            "title": "2023 ESC/ESH Guidelines for Hypertension Management",
            "organization": "European Society of Cardiology",
            "year": 2023,
            "sections": {
                "treatment": {
                    "content": "Combination therapy preferred for most patients to improve adherence.",
                    "key_points": [
                        "Start with two-drug combination for most patients",
                        "ACE-I or ARB + CCB or diuretic",
                        "Single pill combinations improve adherence"
                    ]
                }
            }
        }
    }
    
    # Save guidelines to files
    for category, guidelines in [
        ("cardiology", cardiology_guidelines),
        ("diabetes", diabetes_guidelines),
        ("hypertension", hypertension_guidelines)
    ]:
        category_path = base_path / category
        category_path.mkdir(parents=True, exist_ok=True)
        
        for guideline_id, guideline_data in guidelines.items():
            file_path = category_path / f"{guideline_id}.json"
            with open(file_path, 'w') as f:
                json.dump(guideline_data, f, indent=2)
            print(f"Created: {file_path}")


def create_rag_corpus():
    """Create sample medical literature corpus"""
    
    base_path = Path("data/rag_corpus")
    base_path.mkdir(parents=True, exist_ok=True)
    
    # Sample medical literature entries
    literature = [
        {
            "id": "pmid35000001",
            "title": "ACE Inhibitors in Diabetic Nephropathy: A Meta-Analysis",
            "abstract": "ACE inhibitors reduce progression of diabetic nephropathy and decrease proteinuria. Studies show 30-40% reduction in progression to ESRD. Monitor potassium and creatinine 1-2 weeks after initiation. A rise in creatinine up to 30% is acceptable and indicates hemodynamic effect.",
            "journal": "NEJM",
            "year": 2023,
            "keywords": ["ACE inhibitor", "diabetic nephropathy", "CKD", "proteinuria"],
            "key_findings": [
                "ACE-I reduce albuminuria by 40% on average",
                "Benefits seen across all CKD stages",
                "Acceptable Cr rise: up to 30% in first 2 months",
                "Monitor K+ closely - risk of hyperkalemia with eGFR <45"
            ]
        },
        {
            "id": "pmid35000002",
            "title": "GLP-1 Receptor Agonists and Cardiovascular Outcomes",
            "abstract": "GLP-1 RAs demonstrate significant cardiovascular benefit in patients with type 2 diabetes. Semaglutide, liraglutide, and dulaglutide reduce MACE by 12-26%. Also provide modest weight loss (5-10 kg) and A1c reduction (1-1.5%).",
            "journal": "Lancet",
            "year": 2024,
            "keywords": ["GLP-1", "cardiovascular disease", "diabetes", "MACE"],
            "key_findings": [
                "Semaglutide: 26% MACE reduction in SUSTAIN-6",
                "Liraglutide: 13% MACE reduction in LEADER trial",
                "Benefits independent of glycemic control",
                "Renal protection: 20-30% reduction in albuminuria"
            ]
        },
        {
            "id": "pmid35000003",
            "title": "SGLT2 Inhibitors in Heart Failure: EMPEROR and DAPA-HF Trials",
            "abstract": "SGLT2 inhibitors reduce HF hospitalizations and CV death in both HFrEF and HFpEF. Benefits seen regardless of diabetes status. Empagliflozin and dapagliflozin reduce HF hospitalizations by 30%.",
            "journal": "Circulation",
            "year": 2023,
            "keywords": ["SGLT2 inhibitor", "heart failure", "HFrEF", "HFpEF"],
            "key_findings": [
                "30% reduction in HF hospitalization",
                "Benefits in diabetes and non-diabetes patients",
                "Start early in HF treatment algorithm",
                "Minimal side effects - genital infections most common"
            ]
        },
        {
            "id": "pmid35000004",
            "title": "Hypertension Management in Chronic Kidney Disease",
            "abstract": "BP control is critical in CKD to slow progression. Target BP <130/80 if proteinuria present. ACE-I or ARB are first-line agents. Monitor K+ and Cr closely. Combination therapy often needed.",
            "journal": "JASN",
            "year": 2024,
            "keywords": ["hypertension", "CKD", "ACE inhibitor", "ARB"],
            "key_findings": [
                "Target BP <130/80 in CKD with proteinuria",
                "ACE-I/ARB reduce proteinuria and slow CKD progression",
                "Risk of hyperkalemia increases with eGFR <45",
                "May need 2-3 agents for BP control in CKD"
            ]
        },
        {
            "id": "pmid35000005",
            "title": "Drug-Drug Interactions in Polypharmacy: Focus on Antihypertensives",
            "abstract": "Common interactions include ACE-I + spironolactone (hyperkalemia), NSAIDs + ACE-I (renal impairment), and diuretics + lithium (toxicity). Always review medication list for potential interactions.",
            "journal": "Pharmacotherapy",
            "year": 2023,
            "keywords": ["drug interactions", "polypharmacy", "antihypertensives"],
            "key_findings": [
                "ACE-I + K-sparing diuretics: Major hyperkalemia risk",
                "NSAIDs worsen HTN control and renal function",
                "Beta-blockers may mask hypoglycemia symptoms",
                "Monitor renal function and electrolytes closely"
            ]
        },
        {
            "id": "pmid35000006",
            "title": "Diabetes and Cardiovascular Risk: The Cardio-Renal-Metabolic Syndrome",
            "abstract": "Type 2 diabetes increases CV risk 2-4 fold. Multi-pronged approach needed: glycemic control, BP management, lipid control, and use of cardioprotective agents (GLP-1, SGLT2i).",
            "journal": "JACC",
            "year": 2024,
            "keywords": ["diabetes", "cardiovascular risk", "CRM syndrome"],
            "key_findings": [
                "Comprehensive risk factor management essential",
                "Statin therapy for all diabetes patients >40 years",
                "GLP-1 RA or SGLT2i preferred after metformin",
                "BP target <130/80 in diabetes"
            ]
        },
        {
            "id": "pmid35000007",
            "title": "Renal Dosing of Common Medications in CKD",
            "abstract": "Many medications require dose adjustment in CKD. ACE-I, ARBs, metformin, and gabapentin are commonly misdosed. Use eGFR for dosing decisions. Some drugs contraindicated at low eGFR.",
            "journal": "Kidney International",
            "year": 2023,
            "keywords": ["renal dosing", "CKD", "medication safety"],
            "key_findings": [
                "Metformin: Avoid if eGFR <30",
                "Gabapentin: Reduce dose by 50% if eGFR <60",
                "NSAIDs: Avoid in CKD stage 4-5",
                "Lisinopril: Start 5-10mg if eGFR <30, max 40mg"
            ]
        },
        {
            "id": "pmid35000008",
            "title": "Combination Antihypertensive Therapy: Evidence and Practice",
            "abstract": "Most patients need 2-3 antihypertensives for BP control. Rational combinations: ACE-I + CCB, ACE-I + diuretic. Avoid ACE-I + ARB (no added benefit, increased adverse events).",
            "journal": "Hypertension",
            "year": 2024,
            "keywords": ["combination therapy", "hypertension", "polypharmacy"],
            "key_findings": [
                "ACE-I + CCB: Excellent combination, complementary mechanisms",
                "ACE-I + thiazide: Proven benefit, watch K+ and Cr",
                "Avoid ACE-I + ARB: Increased hyperkalemia, no benefit",
                "Single-pill combinations improve adherence"
            ]
        }
    ]
    
    # Save to JSONL format
    corpus_path = base_path / "medical_literature.jsonl"
    with open(corpus_path, 'w') as f:
        for entry in literature:
            f.write(json.dumps(entry) + '\n')
    
    print(f"Created: {corpus_path}")
    print(f"Total documents: {len(literature)}")


if __name__ == "__main__":
    print("Setting up medical guidelines database...")
    create_guidelines_database()
    
    print("\nSetting up medical literature corpus...")
    create_rag_corpus()
    
    print("\n✓ Data setup complete!")
    print("\nNext steps:")
    print("1. Guidelines are stored in data/guidelines/")
    print("2. Medical literature is in data/rag_corpus/")
    print("3. Run the application with: streamlit run app.py")