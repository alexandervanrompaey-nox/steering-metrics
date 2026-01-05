from abc import abstractmethod, ABC
from arrow import Arrow



class IMeasurementRepo(ABC):

    @abstractmethod
    def get_measurements(self, device_id: str, since: Arrow, until: Arrow):
        raise NotImplementedError