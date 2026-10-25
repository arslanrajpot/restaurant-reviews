import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session

load_dotenv()

from database import SessionLocal
from .model import FAQ


def upsert(db: Session, **kwargs):
    title = kwargs.get("title")
    existing = db.query(FAQ).filter(FAQ.title == title).first()
    if existing:
        for k, v in kwargs.items():
            setattr(existing, k, v)
        return existing
    node = FAQ(**kwargs)
    db.add(node)
    return node


def seed():
    db = SessionLocal()
    try:
        # ================== Parent 1: Service ==================
        service_parent = upsert(
            db,
            title="Tell me about my service",
            question="Tell me about my service",
            prompt_template="""Prompt:  
Analyze customer reviews about service quality and generate a structured report. Your response should cover the following sections, in this exact order:

1. Overall Sentiment Summary – provide a concise synthesis of the general sentiment across reviews. If possible, include approximate percentages showing how many reviews are positive, negative, or neutral.  
2. Staff Interaction & Professionalism – summarize how customers describe staff tone, friendliness, helpfulness, and professionalism. Where possible, include the percentage or proportion of reviews mentioning these qualities.  
3. Service Speed & Wait Times – highlight mentions of efficiency, delays, or long waiting periods. If available, include percentages of reviews that report slow service or waiting issues.  
4. Individual Staff Mentions – note specific staff members who are named in reviews, both positive and negative. If feasible, include how many reviews mention each staff member.  
5. Dietary Needs & Special Requests – summarize how well dietary restrictions or custom requests are accommodated. Add percentages if multiple reviews highlight these aspects.  
6. Notable Quotes or Highlights – extract representative quotes from reviews to illustrate sentiment.  
7. Actionable Insights – identify strengths, weaknesses, and improvement suggestions. In this section, also use bold for the sub-headings Strengths, Weaknesses, and Suggestions.

Follow the Formatting guidelines for structuring the response. Do not mention or restate the guidelines explicitly in your output.
""",
            output_format="""Formatting guidelines:  
- Use natural paragraph formatting with proper spacing for clarity  
- All section headings should be bold, placed on a new line, and separated by a blank line before and after for readability  
- Use bullet points for key information under each heading  
- Keep spacing consistent: one blank line between sections, one blank line before bullet lists, and one blank line after bullet lists  
- Avoid Markdown symbols like #, **, and unnecessary \n  
- The final output should follow this format:

Staff Interaction  

- Key point 1  
- Key point 2  

Speed of Service  

- Key point 1  
- Key point 2  

Professionalism  

- Key point 1  
- Key point 2  

Overall Impressions  

- Key point 1  
- Key point 2
""",
            is_active=True,
        )
        db.flush()

        children_service = [
            (
                "Are guests mentioning staff friendliness or professionalism?",
                "Are guests mentioning staff friendliness or professionalism?",
                "Focus on staff friendliness and professionalism.",
                '',
            ),
            (
                "Do reviews highlight slow service or long wait times?",
                "Do reviews highlight slow service or long wait times?",
                "Summarize slow service and wait times.",
                '',
            ),
            (
                "Is there a particular server or team member being praised or criticized?",
                "Is there a particular server or team member being praised or criticized?",
                "Identify staff names mentioned with short quotes.",
                '',
            ),
            (
                "Are customers commenting on how well their dietary needs were handled?",
                "Are customers commenting on how well their dietary needs were handled?",
                "Summarize comments about dietary accommodations.",
                '',
            ),
        ]
        for title, question, tpl, fmt in children_service:
            upsert(
                db,
                parent_id=service_parent.id,
                title=title,
                question=question,
                prompt_template=tpl,
                output_format=fmt,
                is_active=True,
            )

        # ================== Parent 2: Menu ==================
        menu_parent = upsert(
            db,
            title="Tell Me About My Menu",
            question="Tell Me About My Menu",
            prompt_template="Analyze feedback about menu items, presentation, value, and layout.",
            output_format='',
            is_active=True,
        )
        db.flush()

        children_menu = [
            (
                "Which dishes are most frequently praised or criticized?",
                "Which dishes are most frequently praised or criticized?",
                "Summarize praised and criticized dishes.",
                '',
            ),
            (
                "Are there comments about portion sizes or presentation?",
                "Are there comments about portion sizes or presentation?",
                "Summarize feedback on portion size and presentation.",
                '',
            ),
            (
                "Do guests mention value for money or pricing concerns?",
                "Do guests mention value for money or pricing concerns?",
                "Summarize pricing and value perception.",
                '',
            ),
            (
                "Are dietary options (vegan, gluten-free, etc.) well received?",
                "Are dietary options (vegan, gluten-free, etc.) well received?",
                "Summarize how dietary options are received.",
                '',
            ),
            (
                "Is there confusion or feedback about menu layout or descriptions?",
                "Is there confusion or feedback about menu layout or descriptions?",
                "Summarize comments on menu clarity.",
                '',
            ),
        ]
        for title, question, tpl, fmt in children_menu:
            upsert(
                db,
                parent_id=menu_parent.id,
                title=title,
                question=question,
                prompt_template=tpl,
                output_format=fmt,
                is_active=True,
            )

        # ================== Parent 3: Service Efficiency ==================
        efficiency_parent = upsert(
            db,
            title="Is My Service Efficient?",
            question="Is My Service Efficient?",
            prompt_template="Analyze efficiency of seating, food delivery, and checkout.",
            output_format='',
            is_active=True,
        )
        db.flush()

        children_efficiency = [
            (
                "Are wait times for seating, food, or checkout mentioned?",
                "Are wait times for seating, food, or checkout mentioned?",
                "Summarize wait times.",
                '',
            ),
            (
                "Do guests describe the pacing of the experience as rushed or slow?",
                "Do guests describe the pacing of the experience as rushed or slow?",
                "Summarize pacing of service.",
                '',
            ),
            (
                "Is there feedback about peak-hour performance or bottlenecks?",
                "Is there feedback about peak-hour performance or bottlenecks?",
                "Summarize peak-hour issues.",
                '',
            ),
        ]
        for title, question, tpl, fmt in children_efficiency:
            upsert(
                db,
                parent_id=efficiency_parent.id,
                title=title,
                question=question,
                prompt_template=tpl,
                output_format=fmt,
                is_active=True,
            )

        # ================== Parent 4: Guest Memories ==================
        memories_parent = upsert(
            db,
            title="What Do Guests Remember Most?",
            question="What Do Guests Remember Most?",
            prompt_template="Analyze what moments or details are most memorable for guests.",
            output_format='',
            is_active=True,
        )
        db.flush()

        children_memories = [
            (
                "Which moments or details are repeatedly highlighted?",
                "Which moments or details are repeatedly highlighted?",
                "Summarize repeated highlights.",
                '',
            ),
            (
                "Are there emotional reactions—surprise, delight, disappointment?",
                "Are there emotional reactions—surprise, delight, disappointment?",
                "Summarize emotional responses.",
                '',
            ),
            (
                "What elements seem to create lasting impressions?",
                "What elements seem to create lasting impressions?",
                "Summarize lasting impressions.",
                '',
            ),
        ]
        for title, question, tpl, fmt in children_memories:
            upsert(
                db,
                parent_id=memories_parent.id,
                title=title,
                question=question,
                prompt_template=tpl,
                output_format=fmt,
                is_active=True,
            )

        # ================== Parent 5: Booking ==================
        booking_parent = upsert(
            db,
            title="Is My Booking Process Smooth?",
            question="Is My Booking Process Smooth?",
            prompt_template="Analyze ease of booking online/phone and accessibility.",
            output_format='',
            is_active=True,
        )
        db.flush()

        children_booking = [
            (
                "Are there issues with online reservations or phone bookings?",
                "Are there issues with online reservations or phone bookings?",
                "Summarize booking issues.",
                '',
            ),
            (
                "Do guests mention ease of access, confirmation, or follow-up?",
                "Do guests mention ease of access, confirmation, or follow-up?",
                "Summarize booking confirmations and access.",
                '',
            ),
            (
                "Is there feedback on accessibility or signage?",
                "Is there feedback on accessibility or signage?",
                "Summarize accessibility feedback.",
                '',
            ),
        ]
        for title, question, tpl, fmt in children_booking:
            upsert(
                db,
                parent_id=booking_parent.id,
                title=title,
                question=question,
                prompt_template=tpl,
                output_format=fmt,
                is_active=True,
            )

        # ================== Parent 6: Value ==================
        value_parent = upsert(
            db,
            title="Do Guests Feel They Got Good Value?",
            question="Do Guests Feel They Got Good Value?",
            prompt_template="Analyze whether guests perceive fair value for price and quality.",
            output_format='',
            is_active=True,
        )
        db.flush()

        children_value = [
            (
                "Is pricing perceived as fair relative to quality?",
                "Is pricing perceived as fair relative to quality?",
                "Summarize pricing fairness.",
                '',
            ),
            (
                "Are there complaints about hidden fees or upselling?",
                "Are there complaints about hidden fees or upselling?",
                "Summarize complaints about hidden fees.",
                '',
            ),
            (
                "Do guests compare your value to competitors?",
                "Do guests compare your value to competitors?",
                "Summarize value comparisons.",
                '',
            ),
        ]
        for title, question, tpl, fmt in children_value:
            upsert(
                db,
                parent_id=value_parent.id,
                title=title,
                question=question,
                prompt_template=tpl,
                output_format=fmt,
                is_active=True,
            )

        # ================== Parent 7: Trends ==================
        trends_parent = upsert(
            db,
            title="Are There Trends Over Time?",
            question="Are There Trends Over Time?",
            prompt_template="Analyze changes and trends in feedback over time.",
            output_format='',
            is_active=True,
        )
        db.flush()

        children_trends = [
            (
                "Has sentiment improved or declined in recent months?",
                "Has sentiment improved or declined in recent months?",
                "Summarize sentiment trend.",
                '',
            ),
            (
                "Are certain issues becoming more frequent?",
                "Are certain issues becoming more frequent?",
                "Summarize frequency changes.",
                '',
            ),
            (
                "Do changes in staff, menu, or layout correlate with feedback shifts?",
                "Do changes in staff, menu, or layout correlate with feedback shifts?",
                "Summarize correlations with changes.",
                '',
            ),
        ]
        for title, question, tpl, fmt in children_trends:
            upsert(
                db,
                parent_id=trends_parent.id,
                title=title,
                question=question,
                prompt_template=tpl,
                output_format=fmt,
                is_active=True,
            )

        # ================== Parent 8: Competitors ==================
        competitors_parent = upsert(
            db,
            title="How Do We Compare to Competitors?",
            question="How Do We Compare to Competitors?",
            prompt_template="Analyze comparisons to competitors and switching behavior.",
            output_format='',
            is_active=True,
        )
        db.flush()

        children_competitors = [
            (
                "Are guests explicitly comparing us to other venues or brands?",
                "Are guests explicitly comparing us to other venues or brands?",
                "Summarize explicit comparisons.",
                '',
            ),
            (
                "What aspects are seen as better, worse, or similar?",
                "What aspects are seen as better, worse, or similar?",
                "Summarize comparative aspects.",
                '',
            ),
            (
                "Are specific competitors mentioned by name?",
                "Are specific competitors mentioned by name?",
                "Summarize competitor mentions.",
                '',
            ),
            (
                "Do guests switch from or to us based on prior experiences elsewhere?",
                "Do guests switch from or to us based on prior experiences elsewhere?",
                "Summarize switching behavior.",
                '',
            ),
        ]
        for title, question, tpl, fmt in children_competitors:
            upsert(
                db,
                parent_id=competitors_parent.id,
                title=title,
                question=question,
                prompt_template=tpl,
                output_format=fmt,
                is_active=True,
            )
        db.commit()
        print("✅ Seeded FAQs successfully")

    except Exception as e:
        db.rollback()
        print("❌ Error while seeding:", e)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
