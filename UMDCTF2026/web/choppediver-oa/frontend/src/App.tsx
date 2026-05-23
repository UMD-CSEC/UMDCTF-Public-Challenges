import { useState } from "react";
import { useChoppediver } from "./lib/ws";
import { Intro } from "./components/Intro";
import { Instructions } from "./components/Instructions";
import { Round } from "./components/Round";
import { Rejection } from "./components/Rejection";
import { Pass } from "./components/Pass";
import { Awaiting } from "./components/Awaiting";
import { Lost } from "./components/Lost";

export function App() {
  const { state, start, submit, ready, total, keepalive } = useChoppediver();
  const [instructionsDismissed, setInstructionsDismissed] = useState(false);

  const onInstructionsContinue = () => {
    setInstructionsDismissed(true);
    ready();
  };

  const renderPhase = () => {
    switch (state.phase) {
      case "idle":
        return <Intro onStart={start} connecting={false} />;
      case "connecting":
        return <Intro onStart={() => {}} connecting={true} />;
      case "awaiting":
      case "round":
        if (!instructionsDismissed) {
          return (
            <Instructions
              onContinue={onInstructionsContinue}
              totalRounds={total}
            />
          );
        }
        if (state.phase === "awaiting") {
          return <Awaiting round={state.round} total={total} keepalive={keepalive} />;
        }
        return (
          <Round
            round={state.round}
            chartUrl={state.chartUrl}
            deadline={state.deadline}
            onAnswer={submit}
            keepalive={keepalive}
          />
        );
      case "reject":
        return <Rejection reason={state.reason} />;
      case "pass":
        return <Pass flag={state.flag} />;
      case "lost":
        return <Lost reason={state.reason} />;
    }
  };

  return renderPhase();
}
