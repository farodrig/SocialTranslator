import logging

from datetime import timedelta, date

from django.conf import settings
from django.db.models import Count
from django.db.models.functions import TruncDate

from scipy.optimize import minimize
import numpy as np

from preferences.utils import triple_exponential_smoothing, meanSquareError
from translator.models import InteractionLog

logger = logging.getLogger(__name__)

class UserPreferences():

    interval = settings.PREFERENCES_INTERVAL
    forecast_len = settings.PREFERENCES_FORECAST

    def __init__(self, sender, social, receiver = None):
        self.sender = sender
        self.receiver = receiver
        self.social = social
        self.serie = np.zeros((self.interval, ), dtype=np.int)
        self.hw_serie = np.zeros((self.interval, ), dtype=np.int)
        self.forecast = np.zeros((self.forecast_len, ), dtype=np.int)
        self.alpha = 1.
        self.beta = 1.
        self.gamma = 1.
        self.updateSerie()
        self.updateHoltWinterSerie()

    def updateSerie(self):
        if self.receiver is not None:
            interactions = InteractionLog.objects.filter(fromUser=self.sender, toUser=self.receiver, through=self.social)
        else:
            interactions = InteractionLog.objects.filter(fromUser=self.sender, through=self.social)

        interactions = interactions.annotate(date=TruncDate('timestamp')).values("date").annotate(qt=Count('id')).order_by("-date")
        pars = []
        today = date.today()
        for i in range(0, 365):
            pars.insert(0, (today-timedelta(i), 0))

        self.serie = np.empty(self.interval)
        i = 0
        for par in pars:
            saved = False
            for interaction in interactions:
                if par[0] == interaction['date']:
                    self.serie[i] = interaction['qt']
                    saved = True
                    break
            if not saved:
                self.serie[i] = 0
            i += 1

    def updateHoltWinterSerie(self):
        guess = np.ndarray((3,), buffer=np.array([self.alpha, self.beta, self.gamma]), dtype=float)
        optimals = minimize(self.predictionsMSE, guess, bounds=[(0,1), (0,1), (0,1)])
        if not optimals.success:
            logger.info(optimals.message)
            return
        optimals = optimals.x
        self.hw_serie, self.forecast = triple_exponential_smoothing(self.serie, 7, optimals[0], optimals[1], optimals[2], self.forecast_len)
        self.alpha = optimals[0]
        self.beta = optimals[1]
        self.gamma = optimals[2]

    def predictionsMSE(self, greeks):
        hw_serie, forecast = triple_exponential_smoothing(self.serie, 7, greeks[0], greeks[1], greeks[2], 0)
        return meanSquareError(self.serie, hw_serie)

    def update(self):
        self.updateSerie()
        self.updateHoltWinterSerie()