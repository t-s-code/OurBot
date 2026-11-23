# jobs/member_inactivity_job.py

class MemberInactivityJob:
    def __init__(self, discord_client, database, config):
        self._discord_client = discord_client
        self._database = database
        self._config = config

    async def run(self):
        pass
