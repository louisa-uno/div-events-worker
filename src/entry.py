from workers import Response, WorkerEntrypoint, fetch
from urllib.parse import urlparse

class Default(WorkerEntrypoint):
	async def fetch(self, request):
		path = urlparse(request.url).path
  
		# Creates a list of calendars to fetch
		filename = path.lstrip('/').replace('.ics', '')
		if "-" not in filename:
			return Response("Invalid request", status=400)
		else:
			parts = filename.split('-')
		if len(parts) != len(set(parts)):
			return Response("Duplicate calendars are not allowed", status=400)

		# Fetches and combines the calendars
		text = None
		for part in parts:
			url = f"https://raw.githubusercontent.com/louisa-uno/div-events/refs/heads/auto-update/calendars/{part}.ics"
			response = await fetch(url)
			if response.status != 200:
				return Response(f"Could not fetch calendar {part}", status=404)
			response_text = await response.text()
			if text:
				text = text.replace("END:VCALENDAR", "") + response_text.replace("BEGIN:VCALENDAR", "").replace("VERSION:2.0", "").replace("PRODID:ics.py - http://git.io/lLljaA", "") + "\n"
			else:
				text = response_text
		if text:
			return Response(text, headers={"Content-Type": "text/calendar"})
		return Response("No calendars found", status=404)
	