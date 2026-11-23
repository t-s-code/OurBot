# jobs/member_inactivity_job.py

class MemberInactivityJob:
    def __init__(self, discord_client, database, config):
        self._discord_client = discord_client
        self._database = database
        self._config = config

    async def run(self):
        # read all member activity records from db
        # for each record:
            # if the member posted within the last X days, continue
            # get the member's roles
            # if they have the Member role and not the  Established Member role convert them to thr inactive role
        pass
