import {existsSync,readFileSync,writeFileSync} from 'node:fs';
import {randomBytes} from 'node:crypto';
const target=new URL('../.env',import.meta.url);
if(existsSync(target)){console.log('Se conserva el archivo .env existente.');}
else{const example=readFileSync(new URL('../.env.example',import.meta.url),'utf8');writeFileSync(target,example.replace('replace-with-a-random-password',randomBytes(24).toString('hex')).replace('replace-with-at-least-32-random-characters',randomBytes(32).toString('hex')),{flag:'wx'});console.log('Entorno local creado con secretos aleatorios. No se ha mostrado ninguna clave.');}
