#!/usr/bin/env node

/**
 * Converts Celsius to Fahrenheit
 * @param {number} celsius - Temperature in Celsius
 * @returns {number} Temperature in Fahrenheit
 */
function toFahrenheit(celsius) {
  return (celsius * 9/5) + 32;
}

/**
 * Converts Fahrenheit to Celsius
 * @param {number} fahrenheit - Temperature in Fahrenheit
 * @returns {number} Temperature in Celsius
 */
function toCelsius(fahrenheit) {
  return (fahrenheit - 32) * 5/9;
}

/**
 * CLI handler for temperature conversion
 */
function cli() {
  const args = process.argv.slice(2);

  const toCelsiusIndex = args.indexOf('--to-celsius');
  const toFahrenheitIndex = args.indexOf('--to-fahrenheit');

  // Check for invalid combinations
  if ((toCelsiusIndex === -1 && toFahrenheitIndex === -1) ||
      (toCelsiusIndex !== -1 && toFahrenheitIndex !== -1)) {
    console.error('Usage: convert.js --to-celsius <value> | --to-fahrenheit <value>');
    process.exit(1);
  }

  if (toCelsiusIndex !== -1) {
    const value = parseFloat(args[toCelsiusIndex + 1]);
    if (isNaN(value)) {
      console.error('Usage: convert.js --to-celsius <value> | --to-fahrenheit <value>');
      process.exit(1);
    }
    console.log(`${toCelsius(value).toFixed(1)}°C`);
  } else {
    const value = parseFloat(args[toFahrenheitIndex + 1]);
    if (isNaN(value)) {
      console.error('Usage: convert.js --to-celsius <value> | --to-fahrenheit <value>');
      process.exit(1);
    }
    console.log(`${toFahrenheit(value).toFixed(1)}°F`);
  }
}

// Run CLI if this file is executed directly
if (require.main === module) {
  cli();
}

module.exports = { toFahrenheit, toCelsius };
