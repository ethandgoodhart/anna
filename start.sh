# turn on spotify
open -a "Spotify"

# Run all services concurrently
(cd desktop && npm run start) & \
(cd anna-integrations && python3 openai_handler.py) & \
(cd anna-integrations && python3 router.py) & \
wait