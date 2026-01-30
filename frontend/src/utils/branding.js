import { palette } from '@primeuix/themes';

export const applyBrandColor = (hex) => {
    if (!hex) return;

    // Ensure hex starts with #
    const color = hex.startsWith('#') ? hex : `#${hex}`;

    try {
        const colors = palette(color);
        const root = document.documentElement;

        // Define variable mapping based on PrimeVue Aura theme structure
        // The palette function returns keys like '50', '100', etc.
        if (colors && typeof colors === 'object') {
            Object.entries(colors).forEach(([key, value]) => {
                root.style.setProperty(`--p-primary-${key}`, value);
            });
        }
    } catch (e) {
        console.error('Failed to generate palette from brand color', e);
    }
}
