export class CarouselState {
  readonly #length: number;
  readonly #intervalMs: number;
  #interval: ReturnType<typeof setInterval> | undefined;

  current = $state(0);

  constructor(length: number, intervalMs: number) {
    this.#length = length;
    this.#intervalMs = intervalMs;
  }

  prev = () => {
    this.current = (this.current - 1 + this.#length) % this.#length;
    this.#resetInterval();
  };

  next = () => {
    this.current = (this.current + 1) % this.#length;
    this.#resetInterval();
  };

  goTo = (index: number) => {
    this.current = index;
    this.#resetInterval();
  };

  start() {
    this.#interval = setInterval(this.next, this.#intervalMs);
  }

  stop() {
    clearInterval(this.#interval);
  }

  #resetInterval() {
    this.stop();
    this.start();
  }
}
