import { Directive, HostListener, Renderer2 } from '@angular/core';

@Directive({
  selector: '[clickBoom]'
})
export class ClickBoomDirective {

  private audio = new Audio('./assets/boom.mp3');

  constructor(private renderer: Renderer2) {}

  @HostListener('document:click', ['$event'])
  onClick(event: MouseEvent) {
    this.playSound();
    this.createExplosion(event.clientX, event.clientY);
  }

  playSound() {
    this.audio.currentTime = 0;
    this.audio.play().catch(err => {
      console.warn('Audio play failed:', err);
    });
  }

  createExplosion(x: number, y: number) {
    const numParticles = 30;

    for (let i = 0; i < numParticles; i++) {
      const particle = this.renderer.createElement('div');
      particle.classList.add('boom-particle');

      const dx = Math.random() * 3 - 1;
      const dy = Math.random() * 3 - 1;
      particle.style.setProperty('--dx', dx.toString());
      particle.style.setProperty('--dy', dy.toString());

      const size = 12 + Math.random() * 10;
      particle.style.width = `${size}px`;
      particle.style.height = `${size}px`;

      const colors = ['#ffcc00', '#ff8800', '#ff2200'];
      particle.style.background = colors[Math.floor(Math.random() * colors.length)];

      particle.style.left = `${x}px`;
      particle.style.top = `${y}px`;

      document.body.appendChild(particle);
      setTimeout(() => particle.remove(), 600);
    }
  }
}
