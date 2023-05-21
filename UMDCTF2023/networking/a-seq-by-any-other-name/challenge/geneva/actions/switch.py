from actions.action import Action
from scapy.all import TCP


class SwitchAction(Action):
    """
    Defines the SwitchAction - causes the engine to switch two fields before sending a packet.
    """
    # Do not select the switch action during evolutions
    frequency = 0
    def __init__(self):
        """
        Initializes the switch action.

        Args:
        """
        Action.__init__(self, "switch", "both")
        self.terminal = False
        self.branching = False

    def run(self, packet, logger):
        """
        The sleep action simply passes along the packet it was given with an instruction for how long the engine should sleep before sending it.
        """
        logger.debug("  - Switching seq and ack...")
        seqno = packet.packet[TCP].seq 
        ackno = packet.packet[TCP].ack
        packet.packet[TCP].ack = seqno
        packet.packet[TCP].seq = ackno
        return packet, None

    def __str__(self):
        """
        Returns a string representation.
        """
        s = Action.__str__(self)
        s += "{}" 
        return s

    def parse(self, string, logger):
        """
        Parses a string representation for this object.
        """
        return True
