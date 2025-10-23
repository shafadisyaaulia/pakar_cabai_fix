// Tailwind v4 requires using the `@tailwindcss/postcss` adapter when used as a
// PostCSS plugin. See Tailwind migration notes.
module.exports = {
  plugins: {
    // Remove tailwindcss plugin so PostCSS won't try to execute it in this
    // environment. We'll load Tailwind via the Play CDN in `index.html`.
    autoprefixer: {},
  },
}
