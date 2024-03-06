;;; Tickets for March 28, 2020.

#lang racket

(require "booky.rkt")

(start)

(define t1 (make-ticket #:code "viec"
                        (volume "2022" 30)))

(define t2 (make-ticket #:code "car"
                        (volume "2021" 29)
                        (volume "2022" 28)))

(define t3 (make-ticket #:code "ver"
                        (volume "2020-2022" 41)))

(define t4 (make-ticket #:code "conti"
                        (volume "2020-2022" 41)))

(define t5 (make-ticket #:code "etu"
                        (volume "2020-1" 40)
                        (volume "2020-2" 40)
                        (volume "2021-1" 34)
                        (volume "2021-2" 41)))

(define t6 (make-ticket #:code "chr"
                        (volume "2022" 30)))

(define t7 (make-ticket #:code "oldte"
                        (volume "2020" 45)
                        (volume "2021" 61)))

(define t8 (make-ticket #:code "revhe"
                        (volume "2021-1" 36)
                        (volume "2021-2" 38)))

(define t9 (make-ticket #:code "catbq"
                        (volume "2022" 47)))

(define t10 (make-ticket #:code "cahev"
                        (volume "2020-2021" 33)))

(define t11 (make-ticket #:code "ire"
                        (volume "2021" 38)))

(define t12 (make-ticket #:code "revsr"
                        (volume "2021" 42)))

(define t13 (make-ticket #:code "ques"
                        (volume "2022" 26)))

(define t14 (make-ticket #:code "geof"
                        (volume "2021-1" 41)
                        (volume "2021-2" 43)
                        (volume "2022-1" 41)
                        (volume "2022-2" 41)))

(define t15 (make-ticket #:code "cissq"
                        (volume "2021" 44)))

(define t16 (make-ticket #:code "ephlit"
                        (volume "2013" 33)))

(define t17 (make-ticket #:code "ephlov"
                        (volume "2013-1" 39)
                        (volume "2013-2" 54)))

(define t18 (make-ticket #:code "sourd"
                        (volume "2004-2011" 48)
                        (volume "2012-2022" 36)))

(define t19 (make-ticket #:code "esn"
                        (volume "2013-2015" 43)
                        (volume "2021-2022" 34)))

(define t20 (make-ticket #:code "revtlou"
                        (volume "2021" 52)))

(define t21 (make-ticket #:code "bulaim"
                        (volume "2021-2022" 34)))

(define t22 (make-ticket #:code "bib"
                        (volume "2021" 52)))

(define t23 (make-ticket #:code "pri"
                        (volume "2022" 27)))

(define t24 (make-ticket #:code "comfr"
                        (volume "2022" 44)))

(define t25 (make-ticket #:code "nourt"
                        (volume "2022" 36)))

(define t26 (make-ticket #:code "feun"
                        (volume "2021" 48)))

(define t27 (make-ticket #:code "letams"
                        (volume "2021-2022" 27)))

(define t28 (make-ticket #:code "revtho"
                        (volume "2021" 69)))

(define t29 (make-ticket #:code "ambr"
                        (volume "2022" 38)))

(define t30 (make-ticket #:code "ist"
                        (volume "2012" 33)
                        (volume "2021" 40)))

(define t31 (make-ticket #:code "novv"
                        (volume "2021" 42)))

(define t32 (make-ticket #:code "con"
                        (volume "2021" 33)
                        (volume "2022" 28)))

(define t33 (make-ticket #:code "collc"
                        (volume "2021" 32)))

(define t34 (make-ticket #:code "conpe"
                        (volume "2021-2022" 34)))

(define t35 (make-ticket #:code "revspt"
                        (volume "2021" 47)))

(define t36 (make-ticket #:code "maid"
                        (volume "2021" 62)
                        (volume "2022" 58)))

(define t37 (make-ticket #:code "revben"
                        (volume "2021-2022" 64)))

(define t38 (make-ticket #:code "bulhb"
                        (volume "2020-2021" 40)))

(define t39 (make-ticket #:code "monbi"
                        (volume "2022" 43)))

(pdf #:filename "tickets-200223"
     t1 t2 t3 t4 t5 t6
     'newpage t7 t8 t9 t10 t11
     'newpage t12 t13 t14 t15 t16
     'newpage t17 t18 t19 t20 t21
     'newpage t22 t23 t24 t25 t26
     'newpage t27 t28 t29 t30 t31
     'newpage t32 t33 t34 t35 t36
     'newpage t37 t38 t39)
