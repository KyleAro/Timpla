import { typography } from '../theme/tokens';
import { StyleSheet } from 'react-native';
import { ThemePalette } from '../theme/colors';

export function makeStyles(p: ThemePalette) {
  return StyleSheet.create({
    screen: { flex: 1, backgroundColor: p.background },
    content: { padding: 24, width: '100%', maxWidth: 488, alignSelf: 'center' },
    header: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: 32 },
    headerActions: { flexDirection: 'row', alignItems: 'center', gap: 10 },
    settingsButton: { width: 48, minHeight: 48, borderRadius: 23, backgroundColor: p.secondary, alignItems: 'center', justifyContent: 'center' },
    title: { color: p.text, fontSize: typography.title, fontWeight: '700' },
    section: { color: p.text, fontSize: typography.section, fontWeight: '600', marginBottom: 24 },
    row: { flexDirection: 'row', flexWrap: 'wrap', gap: 12, alignItems: 'center', justifyContent: 'space-between', marginBottom: 28 },
    label: { color: p.text, fontSize: typography.body, fontWeight: '600', marginBottom: 12 },
    nameInput: { minHeight: 54, borderWidth: 1, borderColor: p.border, borderRadius: 14, backgroundColor: p.surface, paddingHorizontal: 16, color: p.text, fontSize: typography.body, marginBottom: 28 },
    chips: { flexDirection: 'row', flexWrap: 'wrap', gap: 10, marginBottom: 30 },
    chip: { borderWidth: 1, borderColor: p.border, borderRadius: 24, minHeight: 48, paddingHorizontal: 16, alignItems: 'center', justifyContent: 'center', backgroundColor: p.surface },
    selected: { backgroundColor: p.chip, borderColor: p.accent },
    chipText: { color: p.text, fontSize: typography.label },
    selectedText: { color: p.accent, fontWeight: '600' },
    add: { flexDirection: 'row', borderWidth: 1, borderColor: p.border, borderRadius: 14, alignItems: 'center', backgroundColor: p.surface },
    input: { flex: 1, minWidth: 0, padding: 16, color: p.text, fontSize: typography.body },
    addButton: { minWidth: 64, minHeight: 52, justifyContent: 'center', alignItems: 'center' },
    linkText: { color: p.accent, fontWeight: '600' },
    note: { color: p.muted, fontSize: typography.label, marginTop: 18, marginBottom: 24 },
    done: { backgroundColor: p.buttonBackground, minHeight: 52, borderRadius: 12, alignItems: 'center', justifyContent: 'center' , paddingVertical: 14 },
    doneText: { color: '#FFF8ED', fontSize: typography.body, fontWeight: '600' },
  });
}

