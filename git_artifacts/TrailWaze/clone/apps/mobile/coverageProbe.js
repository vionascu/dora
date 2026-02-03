module.exports = {
  normalizeTrailName(name) {
    if (!name) {
      return '';
    }
    return String(name).trim().replace(/\s+/g, ' ');
  },
};
