const { normalizeTrailName } = require('../coverageProbe');

describe('coverage probe', () => {
  it('normalizes trail names', () => {
    expect(normalizeTrailName('  Bucegi   Ridge ')).toBe('Bucegi Ridge');
  });
});
