function toFahrenheit(c) { return c * 9/5 + 32; }
function toCelsius(f) { return (f - 32) * 5/9; }
function toKelvin(c) { return c + 273.15; }
function fromKelvin(k) { return k - 273.15; }

if (require.main === module) {
  const args = process.argv.slice(2);
  const flag = args[0];
  const temp = parseFloat(args[1]);
  if (flag === '--to-celsius') console.log(toCelsius(temp).toFixed(1));
  else if (flag === '--to-fahrenheit') console.log(toFahrenheit(temp).toFixed(1));
  else if (flag === '--to-kelvin') console.log(toKelvin(temp).toFixed(1));
  else if (flag === '--from-kelvin') console.log(fromKelvin(temp).toFixed(1));
  else { console.error('Usage: convert --to-celsius|--to-fahrenheit|--to-kelvin|--from-kelvin <temp>'); process.exit(1); }
}

module.exports = { toFahrenheit, toCelsius, toKelvin, fromKelvin };
