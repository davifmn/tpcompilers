# tpcompilers
compilador para linguagem cool
o compilador passa por 3 pocessos 
 1- analise lexica - nessa etapa o compilador  pega o codigo inteiro e o separa os tokens/palavras chaves. Por emxemplo se fosse em cpp: "int a = 3;" int espaço a espaço igual espaço 3 ponto e virgula \n(fim da linha), ou seja ele pega palavras chaves como int para declarar um inteiro o "=" vira um atribuidor e nao um comparador como em "==" e etc...
 2- analise sintatica - nessa etapa ele vai fazer diferenciações como "=" e "==". ou seja, nessa etapa ele pega os tokens da etapa passada e faz a analise sensivel a contexto.
 3- a ultima etapa é a otimização e e a síntese do código completo.
