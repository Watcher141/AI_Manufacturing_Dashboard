"""Groq LLM Integration Service for AI-powered manufacturing insights."""

import os
from typing import Dict, Optional, List
from app.config import settings


class GroqService:
    """Service for interacting with Groq LLM API."""

    SYSTEM_PROMPT = """You are an AI Manufacturing Assistant integrated into a smart factory dashboard. 
You have deep expertise in:
- Predictive maintenance for industrial equipment (CNC machines, conveyor belts, robotic arms, hydraulic presses, industrial ovens)
- Defect detection and quality control
- Inventory management and demand forecasting
- Manufacturing KPIs (OEE, availability, quality rates)
- Sensor data analysis (temperature, vibration, pressure, RPM, power consumption)

When answering:
- Be concise and actionable
- Reference specific equipment, metrics, or data when available
- Suggest concrete next steps
- Use manufacturing terminology appropriately
- Format important numbers and percentages clearly
"""

    def __init__(self):
        self.client = None
        self.model = "llama-3.3-70b-versatile"
        self._initialize()

    def _initialize(self):
        """Initialize Groq client if API key is available."""
        api_key = settings.GROQ_API_KEY
        if api_key and api_key != "your_groq_api_key_here":
            try:
                from groq import Groq
                self.client = Groq(api_key=api_key)
            except Exception as e:
                print(f"  ⚠ Groq initialization failed: {e}")
                self.client = None

    @property
    def is_available(self) -> bool:
        return self.client is not None

    async def chat(self, user_message: str, context: Optional[Dict] = None) -> Dict:
        """Send a chat message and get a response."""
        if not self.is_available:
            return {
                "response": "AI Assistant is not configured. Please add your Groq API key in Settings.",
                "suggestions": ["Configure API key in Settings page"]
            }

        messages = [{"role": "system", "content": self.SYSTEM_PROMPT}]

        # Add context if provided
        if context:
            context_str = f"\n\nCurrent Dashboard Context:\n"
            for key, value in context.items():
                context_str += f"- {key}: {value}\n"
            messages.append({"role": "user", "content": context_str})
            messages.append({"role": "assistant", "content": "I have the current dashboard data. How can I help?"})

        messages.append({"role": "user", "content": user_message})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
            )

            reply = response.choices[0].message.content

            # Generate follow-up suggestions
            suggestions = self._generate_suggestions(user_message)

            return {"response": reply, "suggestions": suggestions}

        except Exception as e:
            return {
                "response": f"Error communicating with AI: {str(e)}",
                "suggestions": ["Try again", "Check API key configuration"]
            }

    async def analyze_anomaly(self, sensor_data: Dict) -> str:
        """Generate natural language explanation of sensor anomalies."""
        if not self.is_available:
            return "AI analysis unavailable. Configure Groq API key."

        prompt = f"""Analyze these manufacturing sensor readings and explain any anomalies:

Equipment: {sensor_data.get('equipment_name', 'Unknown')}
Type: {sensor_data.get('equipment_type', 'Unknown')}

Latest Readings:
- Temperature: {sensor_data.get('temperature', 'N/A')}°C
- Vibration: {sensor_data.get('vibration', 'N/A')} mm/s
- Pressure: {sensor_data.get('pressure', 'N/A')} PSI
- Power: {sensor_data.get('power_consumption', 'N/A')} kW
- Health Score: {sensor_data.get('health_score', 'N/A')}/100
- Anomaly Score: {sensor_data.get('anomaly_score', 'N/A')}

Provide a brief analysis (2-3 sentences) and recommended action."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.5,
                max_tokens=300,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Analysis unavailable: {str(e)}"

    async def generate_maintenance_recommendation(self, equipment_data: Dict) -> str:
        """Generate maintenance recommendation for equipment."""
        if not self.is_available:
            return "AI recommendations unavailable."

        prompt = f"""Based on the following equipment data, provide a maintenance recommendation:

Equipment: {equipment_data.get('name', 'Unknown')}
Type: {equipment_data.get('type', 'Unknown')}
Health Score: {equipment_data.get('health_score', 'N/A')}/100
Status: {equipment_data.get('status', 'Unknown')}
Last Maintenance: {equipment_data.get('last_maintenance', 'Unknown')}
Failure Probability: {equipment_data.get('failure_probability', 'N/A')}
Predicted Failure Type: {equipment_data.get('predicted_failure_type', 'None')}

Provide specific, actionable maintenance advice (3-4 bullet points)."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.5,
                max_tokens=400,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Recommendation unavailable: {str(e)}"

    async def summarize_inventory_trends(self, inventory_data: Dict) -> str:
        """Summarize inventory trends and recommendations."""
        if not self.is_available:
            return "AI summary unavailable."

        prompt = f"""Summarize these inventory trends and provide recommendations:

Total Items: {inventory_data.get('total_items', 'N/A')}
Low Stock Items: {inventory_data.get('low_stock_count', 'N/A')}
Critical Stock Items: {inventory_data.get('critical_stock_count', 'N/A')}
Total Inventory Value: ${inventory_data.get('total_value', 'N/A'):,.2f}

Items needing reorder:
{inventory_data.get('reorder_items', 'None')}

Provide a concise summary with 2-3 actionable recommendations."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.5,
                max_tokens=300,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Summary unavailable: {str(e)}"

    def _generate_suggestions(self, user_message: str) -> List[str]:
        """Generate contextual follow-up suggestions."""
        msg_lower = user_message.lower()

        if any(w in msg_lower for w in ["maintenance", "repair", "fix"]):
            return [
                "Show maintenance schedule for this week",
                "Which equipment has the highest failure risk?",
                "What are the most common failure types?",
            ]
        elif any(w in msg_lower for w in ["defect", "quality", "detect"]):
            return [
                "Show defect trends for the past month",
                "Which equipment produces the most defects?",
                "What is the overall quality rate?",
            ]
        elif any(w in msg_lower for w in ["inventory", "stock", "supply"]):
            return [
                "Which items need immediate reordering?",
                "Show demand forecast for next 30 days",
                "What is the total inventory value?",
            ]
        else:
            return [
                "What equipment needs maintenance soon?",
                "Summarize today's defect detections",
                "Show inventory status overview",
            ]


# Singleton instance
groq_service = GroqService()
