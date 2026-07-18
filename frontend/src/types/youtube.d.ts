interface Window {
  YT: {
    Player: new (
      elementId: string,
      options: {
        height: string;
        width: string;
        videoId: string;
        playerVars?: Record<string, string | number | undefined>;
        events?: {
          onReady?: (event: { target: YT.Player | null }) => void;
          onStateChange?: (event: { data: number }) => void;
          onError?: (event: { data: number }) => void;
        };
      }
    ) => {
      playVideo: () => void;
      pauseVideo: () => void;
      seekTo: (seconds: number, allowSeekAhead: boolean) => void;
      getCurrentTime: () => number;
      mute: () => void;
      unMute: () => void;
      isMuted: () => boolean;
      destroy: () => void;
    };
    PlayerState: {
      UNSTARTED: number;
      BUFFERING: number;
      PLAYING: number;
      PAUSED: number;
      ENDED: number;
      CUED: number;
    };
  };
  onYouTubeIframeAPIReady: (() => void) | undefined;
}
