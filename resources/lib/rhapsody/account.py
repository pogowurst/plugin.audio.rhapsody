from datetime import datetime


class Account(object):
    def __init__(self, data):
        self.can_upgrade_streams = data['canUpgradeStreams']
        self.skip_limit_minutes = data['skipLimitMinutes']
        self.locale = data['locale']
        self.is_trial = data['isTrial']
        self.cobrand = data['cobrand']
        self.expiration_date = data['expirationDate']
        self.can_stream_on_mobile = data['canStreamOnMobile']
        self.can_play_premium_radio = data['canPlayPremiumRadio']
        self.id = data['id']
        self.product_code = data['productCode']
        self.tier_code = data['tierCode']
        self.cocat = data['cocat']
        self.create_date = data['createDate']
        self.is_suspended = data['isSuspended']
        self.total_plays = data['totalPlays']
        self.max_stream_count = data['maxStreamCount']
        self.state = data['state']
        self.email = data['email']
        self.skip_limit = data['skipLimit']
        self.plays_remaining = data['playsRemaining']
        self.can_stream_on_home_device = data['canStreamOnHomeDevice']
        self.is_monthly_play_based_tier = data['isMonthlyPlayBasedTier']
        self.can_stream_on_pc = data['canStreamOnPC']
        self.is_public = data['isPublic']
        self.tier_name = data['tierName']
        self.product_name = data['productName']
        self.catalog = data['catalog']
        self.can_stream_on_web = data['canStreamOnWeb']
        self.is_play_based_tier = data['isPlayBasedTier']
        self.first_name = data['firstName']
        self.last_name = data['lastName']
        self.is_one_time_play_based_tier = data['isOneTimePlayBasedTier']
        self.trial_length_days = data['trialLengthDays']
        self.country = data['country']
        self.logon = data['logon']


class Session(object):
    def __init__(self, data):
        self.id = data['id']
        self.valid = data['valid']
        self.expired_by_client_type = data['expiredByClientType']
        self.created = datetime.now()
