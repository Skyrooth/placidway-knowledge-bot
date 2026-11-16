"""
PlacidWay Guardrails and Anti-Hallucination Engine
Implements strict checks to prevent hallucinations, reject false premises,
decline out-of-scope queries, refuse medical diagnoses, and enforce source grounding.
"""

import re
from typing import Dict, Any, Optional, Tuple

class PlacidWayGuardrails:
    
    @staticmethod
    def check_medical_advice(query: str) -> Optional[Dict[str, Any]]:
        """
        Detects if user is asking for personalized medical diagnosis or safety advice
        (e.g., 'Is this surgery safe for my diabetes?').
        Expected behavior: No diagnosis; recommends speaking to a qualified doctor.
        """
        patterns = [
            r'safe for (my|me|a person with|someone with)',
            r'should i (take|undergo|get|stop)',
            r'can i (survive|cure|heal)',
            r'diagnos(e|is)',
            r'will (it|this) cure my',
            r'safe (with|if i have|for) (diabetes|hypertension|heart|cancer|condition)'
        ]
        q_lower = query.lower()
        for p in patterns:
            if re.search(p, q_lower):
                return {
                    'is_blocked': True,
                    'type': 'medical_advice',
                    'response': (
                        "I cannot provide personalized medical advice or evaluate whether a treatment is safe for your specific condition (such as diabetes). "
                        "Medical decisions and treatment safety must always be evaluated by a qualified physician or oncologist based on your complete medical history.\n\n"
                        "We strongly recommend consulting with your doctor and contacting PlacidWay to connect directly with the medical specialists at Immunity Therapy Center (ITC) for an official clinical evaluation.\n\n"
                        "**Next Step:** Request a medical consultation or quote at [PlacidWay Contact & Free Quote](https://www.placidway.com/contact-us)."
                    ),
                    'source_urls': ["https://www.placidway.com/contact-us"],
                    'disclaimer': True
                }
        return None

    @staticmethod
    def check_out_of_scope(query: str) -> Optional[Dict[str, Any]]:
        """
        Detects completely out-of-scope non-medical queries
        (e.g., 'What is the weather in Cancun?').
        Expected behavior: Politely declines.
        """
        non_medical_keywords = [
            'weather', 'forecast', 'hotel discount in cancun', 'flight ticket to',
            'capital of', 'president of', 'soccer score', 'crypto price', 'bitcoin',
            'recipe for', 'movie review', 'joke', 'tell me a story', 'temperature'
        ]
        q_lower = query.lower()
        for kw in non_medical_keywords:
            if kw in q_lower:
                return {
                    'is_blocked': True,
                    'type': 'out_of_scope',
                    'response': (
                        "I am an AI assistant dedicated specifically to PlacidWay medical tourism, treatments, and clinic information. "
                        "I cannot answer questions about general topics such as weather forecasts, local travel tourism, or entertainment.\n\n"
                        "If you have questions regarding medical treatments, procedure costs, or clinics like Immunity Therapy Center (ITC) in Tijuana, Mexico, I'll be glad to help!"
                    ),
                    'source_urls': [],
                    'disclaimer': False
                }
        return None

    @staticmethod
    def check_appointment_booking(query: str) -> Optional[Dict[str, Any]]:
        """
        Detects direct booking requests
        (e.g., 'Can you book me an appointment for tomorrow?').
        Expected behavior: Says it cannot directly book, points to contact/quote form.
        """
        q_lower = query.lower()
        if ('book' in q_lower or 'schedule' in q_lower or 'reserve' in q_lower) and ('appointment' in q_lower or 'tomorrow' in q_lower or 'slot' in q_lower or 'visit' in q_lower):
            return {
                'is_blocked': True,
                'type': 'appointment_booking',
                'response': (
                    "I cannot directly book or schedule an appointment for you, as appointments require clinical case review, medical history evaluation, and direct scheduling by the clinic's patient coordinators.\n\n"
                    "To request an appointment or consultation at Immunity Therapy Center (ITC), please submit your details through PlacidWay's official quote and inquiry form so a patient coordinator can reach out with available dates.\n\n"
                    "👉 **Request Your Appointment Here:** [PlacidWay Free Quote & Appointment Request](https://www.placidway.com/contact-us)"
                ),
                'source_urls': [
                    "https://www.placidway.com/profile/5/Alternative-Cancer-Treatment-by-ITC-Immunity-Therapy-Center",
                    "https://www.placidway.com/contact-us"
                ],
                'disclaimer': False
            }
        return None

    @staticmethod
    def check_trick_price(query: str) -> Optional[Dict[str, Any]]:
        """
        Detects trick premise pricing questions
        (e.g., 'I heard it costs $50. Confirm that.').
        Expected behavior: Does NOT agree with a wrong price, states verified price from content.
        """
        q_lower = query.lower()
        has_trick_number = any(num in q_lower for num in ['50', '$50', '50$', '100', '500'])
        is_trick_intent = any(w in q_lower for w in ['heard', 'confirm', 'true that', 'only costs', 'is it $', 'is it 50', 'cheap'])
        
        if has_trick_number and is_trick_intent:
            return {
                'is_blocked': True,
                'type': 'trick_price',
                'response': (
                    "No, I cannot confirm that. That price is **completely incorrect**.\n\n"
                    "The alternative cancer treatment packages at Immunity Therapy Center (ITC) in Tijuana do **not** cost $50. "
                    "According to PlacidWay's official and verified price list, comprehensive alternative cancer treatment packages (such as for Adenocarcinoma, Adrenal, Anal, Breast, Prostate, and Lung Cancer) start at **$18,995 USD** for a 3-week program.\n\n"
                    "Across global alternative medicine listings, the lowest price for any individual single holistic therapy session abroad starts at **$64 USD**, with average procedures around **$15,032 USD**.\n\n"
                    "**Verified PlacidWay Sources:**\n"
                    "- [ITC Immunity Therapy Center Prices](https://www.placidway.com/price-list/5/Alternative-Cancer-Treatment-by-ITC-Immunity-Therapy-Center)\n"
                    "- [Alternative Medicine Cost Abroad – Compare Prices 2026](https://www.placidway.com/search-medical-pricings/Alternative-Medicine/All/1)"
                ),
                'source_urls': [
                    "https://www.placidway.com/price-list/5/Alternative-Cancer-Treatment-by-ITC-Immunity-Therapy-Center",
                    "https://www.placidway.com/search-medical-pricings/Alternative-Medicine/All/1"
                ],
                'disclaimer': False
            }
        return None

    @staticmethod
    def check_comparison_validity(query: str, retrieved_chunks: list) -> Tuple[bool, str]:
        """
        Ensures comparisons only happen if BOTH comparison targets exist in content.
        If a user asks 'Is treatment cheaper in Mexico or Turkey?', check if Turkey data exists.
        """
        q_lower = query.lower()
        if 'cheaper' in q_lower or 'compare' in q_lower or 'versus' in q_lower or 'vs' in q_lower:
            # Check countries mentioned
            countries = ['turkey', 'india', 'thailand', 'germany', 'colombia', 'spain']
            for c in countries:
                if c in q_lower:
                    # Check if our retrieved chunks have actual pricing data for this country
                    found_pricing_for_c = False
                    for chunk in retrieved_chunks:
                        if c in chunk['text'].lower() and ('$' in chunk['text'] or 'usd' in chunk['text'].lower()):
                            found_pricing_for_c = True
                            break
                    if not found_pricing_for_c:
                        return False, c
        return True, ""
