describe('Trailwaze mockup', () => {
  beforeAll(async () => {
    await device.launchApp({ newInstance: true });
  });

  it('shows the main UI elements', async () => {
    await expect(element(by.id('app-title'))).toBeVisible();
    await expect(element(by.id('map-placeholder'))).toBeVisible();
    await expect(element(by.id('report-button'))).toBeVisible();
  });
});
