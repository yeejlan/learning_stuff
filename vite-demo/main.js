import './style.css'
import 'virtual:windi.css'
import { spline } from '@georgedoescode/spline';
import { SVG } from '@svgdotjs/svg.js';

document.querySelector('#app').innerHTML = `
  <h1>Hello Vite!</h1>
  <a href="https://vitejs.dev/guide/features.html" target="_blank">Documentation</a>
`

class BlobCharacter {
  constructor(name) {
    this.name = name;
  }

  hello() {
    console.log("hello " + this.name);
  }
}

let bc = new BlobCharacter('sheep')
bc.hello()


