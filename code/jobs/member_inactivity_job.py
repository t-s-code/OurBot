# jobs/member_inactivity_job.py

class MemberInactivityJob:
    def __init__(self, discord_client, database, config):
        self._discord_client = discord_client
        self._database = database
        self._config = config

    async def run(self):
        # TODO 5 - implement
        # read all member activity records from db
        # inactive_date = today - convert_after_days
        # filter down to only records where the member is active and the last post date <= inactive_date
        # for each record:
            # get the member's roles
            # if they are no longer in the guild, Mark their record as inactive
            # elif they have the inactive member role, log unexpected insctive member & mark uodate the record to show they are already inactive
            # elif they have established member role, log "Established member <display name> (user name) hasnt posted in X days"
            # elif they have the member role, remove their member role and add the inactive member role and log "Member converted to inactive"
            # else they somehow dont have any of the roles, log "Expected member to have at least one role: <display name> (user name)"
        # do this with a couple of helper methods, like the ither job, so this method is easy to read
        pass
        # TODO Me:
        # add todo in DB for get all records
        # add todo to add method to log to a log channel
        # add todo to update a members roles
