filename seer9 './yr1973_2014.seer9/*.TXT';                                           
                                                                                      
data in;                                                                              
  infile seer9 lrecl=362;                                                             
  input                                                                               
    @ 1   PUBCSNUM             $char8.  /* Patient ID */                              
    @ 9   REG                  $char10. /* SEER registry */                           
    @ 19  MAR_STAT             $char1.  /* Marital status at diagnosis */             
    @ 20  RACE1V               $char2.  /* Race/ethnicity */                          
    @ 23  NHIADE               $char1.  /* NHIA Derived Hisp Origin */                
    @ 24  SEX                  $char1.  /* Sex */                                     
    @ 25  AGE_DX               $char3.  /* Age at diagnosis */                        
    @ 28  YR_BRTH              $char4.  /* Year of birth */                           
    @ 35  SEQ_NUM              $char2.  /* Sequence number */                         
    @ 37  MDXRECMP             $char2.  /* Month of diagnosis */                      
    @ 39  YEAR_DX              $char4.  /* Year of diagnosis */                       
    @ 43  PRIMSITE             $char4.  /* Primary site ICD-O-2 (1973+) */            
    @ 47  LATERAL              $char1.  /* Laterality */                              
    @ 48  HISTO2V              $char4.  /* Histologic Type ICD-O-2 */                 
    @ 52  BEHO2V               $char1.  /* Behavior Code ICD-O-2*/                    
    @ 53  HISTO3V              $char4.  /* Histologic Type ICD-O-3 */                 
    @ 57  BEHO3V               $char1.  /* Behavior code ICD-O-3 */                   
    @ 58  GRADE                $char1.  /* Grade */                                   
    @ 59  DX_CONF              $char1.  /* Diagnostic confirmation */                 
    @ 60  REPT_SRC             $char1.  /* Type of reporting source */                
    @ 61  EOD10_SZ             $char3.  /* EOD 10 - size (1988+) */                   
    @ 64  EOD10_EX             $char2.  /* EOD 10 - extension */                      
    @ 66  EOD10_PE             $char2.  /* EOD 10 - path extension */                 
    @ 68  EOD10_ND             $char1.  /* EOD 10 - lymph node */                     
    @ 69  EOD10_PN             $char2.  /* EOD 10 - positive lymph nodes examined */  
    @ 71  EOD10_NE             $char2.  /* EOD 10 - number of lymph nodes examined */ 
    @ 73  EOD13                $char13. /* EOD--old 13 digit */                       
    @ 86  EOD2                 $char2.  /* EOD--old 2 digit */                        
    @ 88  EOD4                 $char4.  /* EOD--old 4 digit */                        
    @ 92  EOD_CODE             $char1.  /* Coding system for EOD */                   
    @ 93  TUMOR_1V             $char1.  /* Tumor marker 1 */                          
    @ 94  TUMOR_2V             $char1.  /* Tumor marker 2 */                          
    @ 95  TUMOR_3V             $char1.  /* Tumor marker 3 */                          
    @ 96  CSTUMSIZ             $char3.  /* CS Tumor size */                           
    @ 99  CSEXTEN              $char3.  /* CS Extension */                            
    @ 102 CSLYMPHN             $char3.  /* CS Lymph Nodes */                          
    @ 105 CSMETSDX             $char2.  /* CS Mets at DX */                           
    @ 107 CS1SITE              $char3.  /* CS Site-Specific Factor 1 */               
    @ 110 CS2SITE              $char3.  /* CS Site-Specific Factor 2 */               
    @ 113 CS3SITE              $char3.  /* CS Site-Specific Factor 3 */               
    @ 116 CS4SITE              $char3.  /* CS Site-Specific Factor 4 */               
    @ 119 CS5SITE              $char3.  /* CS Site-Specific Factor 5 */               
    @ 122 CS6SITE              $char3.  /* CS Site-Specific Factor 6 */               
    @ 125 CS25SITE             $char3.  /* CS Site-Specific Factor 25 */              
    @ 128 DAJCCT               $char2.  /* Derived AJCC T */                          
    @ 130 DAJCCN               $char2.  /* Derived AJCC N */                          
    @ 132 DAJCCM               $char2.  /* Derived AJCC M */                          
    @ 134 DAJCCSTG             $char2.  /* Derived AJCC Stage Group */                
    @ 136 DSS1977S             $char1.  /* Derived SS1977 */                          
    @ 137 DSS2000S             $char1.  /* Derived SS2000 */                          
    @ 138 DAJCCFL              $char1.  /* Derived AJCC - flag */                     
    @ 141 CSVFIRST             $char6.  /* CS Version Input Original */               
    @ 147 CSVLATES             $char6.  /* CS Version Derived */                      
    @ 153 CSVCURRENT           $char6.  /* CS Version Input Current */                
    @ 159 SURGPRIF             $char2.  /* RX Summ--surg prim site */                 
    @ 161 SURGSCOF             $char1.  /* RX Summ--scope reg LN sur 2003+*/          
    @ 162 SURGSITF             $char1.  /* RX Summ--surg oth reg/dis */               
    @ 163 NUMNODES             $char2.  /* Number of lymph nodes */                   
    @ 166 NO_SURG              $char1.  /* Reason no cancer-directed surgery */       
    @ 170 SS_SURG              $char2.  /* Site specific surgery (1983-1997) */       
    @ 174 SURGSCOP             $char1.  /* Scope of lymph node surgery 98-02 */        
    @ 175 SURGSITE             $char1.  /* Surgery to other sites */                  
    @ 176 REC_NO               $char2.  /* Record number */                           
    @ 191 TYPE_FU              $char1.  /* Type of followup expected */               
    @ 192 AGE_1REC             $char2.  /* Age recode <1 year olds */                 
    @ 199 SITERWHO             $char5.  /* Site recode ICD-O-3/WHO 2008 */            
    @ 204 ICDOTO9V             $char4.  /* Recode ICD-O-2 to 9 */                     
    @ 208 ICDOT10V             $char4.  /* Recode ICD-O-2 to 10 */                    
    @ 218 ICCC3WHO             $char3.  /* ICCC site recode ICD-O-3/WHO 2008 */       
    @ 221 ICCC3XWHO            $char3.  /* ICCC site rec extended ICD-O-3/ WHO 2008 */ 
    @ 224 BEHTREND             $char1.  /* Behavior recode for analysis */            
    @ 226 HISTREC              $char2.  /* Broad Histology recode */                  
    @ 228 HISTRECB             $char2.  /* Brain recode */                            
    @ 230 CS0204SCHEMA         $char3.  /* CS Schema v0204*/                          
    @ 233 RAC_RECA             $char1.  /* Race recode A */                           
    @ 234 RAC_RECY             $char1.  /* Race recode Y */                           
    @ 235 ORIGRECB             $char1.  /* Origin Recode NHIA */                      
    @ 236 HST_STGA             $char1.  /* SEER historic stage A */                   
    @ 237 AJCC_STG             $char2.  /* AJCC stage 3rd edition (1988+) */          
    @ 239 AJ_3SEER             $char2.  /* SEER modified AJCC stage 3rd ed (1988+) */ 
    @ 241 SSS77VZ              $char1.  /* SEER Summary Stage 1977 (1995-2000) */     
    @ 242 SSSM2KPZ             $char1.  /* SEER Summary Stage 2000 2000 (2001-2003) */
    @ 245 FIRSTPRM             $char1.  /* First malignant primary indicator */       
    @ 246 ST_CNTY              $char5.  /* State-county recode */                     
    @ 255 CODPUB               $char5.  /* Cause of death to SEER site recode */      
    @ 260 CODPUBKM             $char5.  /* COD to site rec KM */                      
    @ 265 STAT_REC             $char1.  /* Vital status recode (study cutoff used) */ 
    @ 266 IHSLINK              $char1.  /* IHS link */                                
    @ 267 SUMM2K               $char1.  /* Historic SSG 2000 Stage */                 
    @ 268 AYASITERWHO          $char2.  /* AYA site recode/WHO 2008 */                
    @ 270 LYMSUBRWHO           $char2.  /* Lymphoma subtype recode/WHO 2008 */        
    @ 272 VSRTSADX             $char1.  /* SEER cause of death classification */      
    @ 273 ODTHCLASS            $char1.  /* SEER other cause of death classification */
    @ 274 CSTSEVAL             $char1.  /* CS EXT/Size Eval */                        
    @ 275 CSRGEVAL             $char1.  /* CS Nodes Eval */                           
    @ 276 CSMTEVAL             $char1.  /* CS Mets Eval */                            
    @ 277 INTPRIM              $char1.  /* Primary by International Rules */          
    @ 278 ERSTATUS             $char1.  /* ER Status Recode Breast Cancer (1990+)*/   
    @ 279 PRSTATUS             $char1.  /* PR Status Recode Breast Cancer (1990+)*/   
    @ 280 CSSCHEMA             $char2.  /* CS Schema - AJCC 6th Edition */            
    @ 282 CS8SITE              $char3.  /* Cs Site-specific Factor 8 */               
    @ 285 CS10SITE             $char3.  /* CS Site-Specific Factor 10*/               
    @ 288 CS11SITE             $char3.  /* CS Site-Specific Factor 11*/               
    @ 291 CS13SITE             $char3.  /* CS Site-Specific Factor 13*/               
    @ 294 CS15SITE             $char3.  /* CS Site-Specific Factor 15*/               
    @ 297 CS16SITE             $char3.  /* CS Site-Specific Factor 16*/               
    @ 300 VASINV               $char1.  /* Lymph-vascular Invasion (2004+)*/          
    @ 301 SRV_TIME_MON         $char4.  /* Survival months */                         
    @ 305 SRV_TIME_MON_FLAG    $char1.  /* Survival months flag */                    
    @ 311 INSREC_PUB           $char1.  /* Insurance Recode (2007+) */                
    @ 312 DAJCC7T              $char3.  /* Derived AJCC T 7th ed */                   
    @ 315 DAJCC7N              $char3.  /* Derived AJCC N 7th ed */                   
    @ 318 DAJCC7M              $char3.  /* Derived AJCC M 7th ed */                   
    @ 321 DAJCC7STG            $char3.  /* Derived AJCC 7 Stage Group */              
    @ 324 ADJTM_6VALUE         $char2.  /* Adjusted AJCC 6th T (1988+) */             
    @ 326 ADJNM_6VALUE         $char2.  /* Adjusted AJCC 6th N (1988+) */             
    @ 328 ADJM_6VALUE          $char2.  /* Adjusted AJCC 6th M (1988+) */             
    @ 330 ADJAJCCSTG           $char2.  /* Adjusted AJCC 6th Stage (1988+) */         
    @ 332 CS7SITE              $char3.  /* CS Site-Specific Factor 7 */               
    @ 335 CS9SITE              $char3.  /* CS Site-specific Factor 9 */               
    @ 338 CS12SITE             $char3.  /* CS Site-Specific Factor 12 */              
    @ 341 HER2                 $char1.  /* Derived HER2 Recode (2010+) */             
    @ 342 BRST_SUB             $char1.  /* Breast Subtype (2010+) */                  
    @ 348 ANNARBOR             $char1.  /* Lymphoma - Ann Arbor Stage (1983+) */      
    @ 349 CSMETSDXB_PUB        $char1.  /* CS mets at DX-bone (2010+) */              
    @ 350 CSMETSDXBR_PUB       $char1.  /* CS mets at DX-brain (2010+) */             
    @ 351 CSMETSDXLIV_PUB      $char1.  /* CS mets at DX-liver (2010+) */             
    @ 352 CSMETSDXLUNG_PUB     $char1.  /* CS mets at DX-lung (2010+) */              
    @ 353 T_VALUE              $char2.  /* T value - based on AJCC 3rd (1988-2003) */ 
    @ 355 N_VALUE              $char2.  /* N value - based on AJCC 3rd (1988-2003) */ 
    @ 357 M_VALUE              $char2.  /* M value - based on AJCC 3rd (1988-2003) */ 
    @ 359 MALIGCOUNT           $char2.  /* Total number of in situ/malignant tumors for patient */        
    @ 361 BENBORDCOUNT         $char2.  /* Total number of benign/borderline tumors for patient */        ;                                                                                 