# Il faut récupérer le total des FP pour cette ligne.
# Il faut récupérer aussi le budget total pour cette ligne 
# et le consommé total des années antérieures également.
# Pour les années passées, on ne distribue pas les FP totaux,
# mais max(FP totaux - (Budget - consommé), 0).
# Pour l'année en cours et celles à venir, on distribue max(Budget - consommé, FP totaux)
#Total des fonds propres pour ce PFI et cet EOTP, pour cet exercice
annee_en_cours = $Exercice.Annee_En_Cours
if $EOTP:
  
else:
  fp_t = sum((m or 0) for m in DIRJAF_F_Conv_Fin_Hist_summary_EOTP_FP_Operation_Exercice_PFI.lookupRecords(
    Operation_Exercice=$Operation_Exercice, PFI=$PFI, FP=True).Montant_Financement)
  conso_passee = sum(m for m in Bdg_DPPI_PPI.lookupRecords(Statut="Consommé", PFI=$PFI).Montant)
  budget_t = 


# Les fonds propres mobilisés pour cette ligne sont égaux à FP totaux moins ceux mobilisés pour les lignes postérieures à celle-ci
# Avec priorité sur l'INVEST
fp_pfi_post = sum(
    (prev.Montant_FP or 0)
    for prev in Bdg_DPPI_PPI.lookupRecords(Operation_Exercice=$Operation_Exercice, PFI=$PFI)
    if prev.Annee > $Annee
)

montant = $Montant or 0

if $DPPI_CB == "INVEST":
  return min(fp_pfi - fp_pfi_post, montant)
else:
  fp_pfi_invest = sum(
      (prev.Montant_FP or 0)
      for prev in Bdg_DPPI_PPI.lookupRecords(Operation_Exercice=$Operation_Exercice, PFI=$PFI, Annee=$Annee, DPPI_CB="INVEST")
  )
  return min(fp_pfi - fp_pfi_post - fp_pfi_invest, montant)l