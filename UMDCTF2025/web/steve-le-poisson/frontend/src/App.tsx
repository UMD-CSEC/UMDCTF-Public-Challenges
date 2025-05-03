import { useCallback, useEffect, useRef, useState } from "react";
import "./App.css";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:3000";

function App() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const audioRef = useRef<HTMLAudioElement>(null);
  const [videoEnded, setVideoEnded] = useState(false);
  const [message, setMessage] = useState("");
  const [guess, setGuess] = useState("");

  const makeGuess = useCallback(async () => {
    const response = await fetch(`${API_URL}/deviner`, {
      headers: {
        'X-Steve-Supposition': guess
      }
    });
    const text = await response.text();

    setMessage(text);
  }, [guess, setMessage]);

  useEffect(() => {
    const video = videoRef.current;
    if (video === null) {
      return;
    }

    video.addEventListener("ended", () => {
      if (audioRef.current !== null) {
        return;
      }

      const audio = new Audio("/audio.mp3");
      audio.addEventListener("canplay", () => {
        setVideoEnded(true);

        audio.loop = true;
        audio.currentTime = 21;
        audio.play();
      }, { once: true });
      audioRef.current = audio;
    }, { once: true });
  }, []);

  if (!videoEnded) {
    return <video ref={videoRef} width="640" height="360" controls>
      <source src="/video.mp4" type="video/mp4" />
    </video>;
  }

  return <>
    <div className="container">
      <h1>Steve Le Poisson</h1>

      <div className="steve">
        <div className="fish-body">
          <div className="eye" />
          <div className="fin" />
        </div>
        <div className="arms" />
        <div className="legs" />
      </div>

      <div className="lyrics">
        <p><strong>[Verset 1]</strong><br/>
        Steve, le- (Poi-)<br/>
        Le poisson Steve (Poisson Steve)<br/>
        Il est orange (Orange, ooh-ooh)<br/>
        Il a des bras, et des jambes<br/>
        Le poisson Steve</p>

        <p><strong>[Pont]</strong><br/>
        Pa-la-la, pa-la-la<br/>
        La-la, la-la, la-la-la<br/>
        La-la, la-la, la-la-la<br/>
        La-la, la-la, la-la, la-la<br/>
        Pa-la-la, pa-la-la</p>

        <p><strong>[Verset 2]</strong><br/>
        Le poisson Steve (Poi-)<br/>
        Il est vraiment très beau (Poisson Steve)<br/>
        Il peut nager sur la Terre (Ooh-ah, ooh-ah)<br/>
        Il peut marcher dans l'eau</p>

        <p><strong>[Outro]</strong><br/>
        Le poisson Steve<br/>
        Il sent forcément mauvais (Mauvais)<br/>
        Mais on l'aime bien</p>
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          makeGuess();
        }}
        className="guess-section"
      >
        <h2>Que veut dire Steve ?</h2>
        <input
          type="text"
          value={guess}
          onChange={(e) => setGuess(e.target.value)}
          placeholder="Tape ta supposition ici..."
        />
        <button type="submit">Deviner</button>
        {message && <p className="response">{message}</p>}
      </form>
    </div>
  </>
}

export default App;