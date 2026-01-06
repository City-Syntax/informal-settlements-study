import pandas as pd

df = pd.read_csv('logger_flags.csv')

print("="*60)
print("RAINBOW FIELD")
print("="*60)
rf = df[df['Settlement']=='Rainbow Field']
print(f"Control Unshaded: {len(rf[(rf['Intervention']=='CONTROL') & (rf['Unshaded']==True)])}")
print(f"Control Shaded: {len(rf[(rf['Intervention']=='CONTROL') & (rf['Shaded']==True)])}")
print(f"MEB Unshaded: {len(rf[(rf['Intervention']=='MEB') & (rf['Unshaded']==True)])}")
print(f"MEB Shaded: {len(rf[(rf['Intervention']=='MEB') & (rf['Shaded']==True)])}")
print(f"RBF Unshaded: {len(rf[(rf['Intervention']=='RBF') & (rf['Unshaded']==True)])}")
print(f"RBF Shaded: {len(rf[(rf['Intervention']=='RBF') & (rf['Shaded']==True)])}")

print("\n" + "="*60)
print("SPORTS COMPLEX")
print("="*60)
sc = df[df['Settlement']=='Sports Complex']
print(f"Control Unshaded: {len(sc[(sc['Intervention']=='CONTROL') & (sc['Unshaded']==True)])}")
print(f"Control Shaded: {len(sc[(sc['Intervention']=='CONTROL') & (sc['Shaded']==True)])}")
print(f"MEB Unshaded: {len(sc[(sc['Intervention']=='MEB') & (sc['Unshaded']==True)])}")
print(f"MEB Shaded: {len(sc[(sc['Intervention']=='MEB') & (sc['Shaded']==True)])}")
print(f"RBF Unshaded: {len(sc[(sc['Intervention']=='RBF') & (sc['Unshaded']==True)])}")
print(f"RBF Shaded: {len(sc[(sc['Intervention']=='RBF') & (sc['Shaded']==True)])}")

print("\n" + "="*60)
print("TOTALS")
print("="*60)
print(f"Rainbow Field - Total: {len(rf)}")
print(f"Sports Complex - Total: {len(sc)}")






