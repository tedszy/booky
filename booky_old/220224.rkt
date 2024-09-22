;;; Tickets for March 28, 2020.

#lang racket

(require "booky.rkt")

(start)

(define t1 (make-ticket #:code "maid"
                        (volume "2023" 56)))

(define t2 (make-ticket #:code "ambr"
                        (volume "2023" 40)))

(define t3 (make-ticket #:code "chr"
                        (volume "2023" 29)))

(define t4 (make-ticket #:code "nourt"
                        (volume "2023" 36)))

(define t5 (make-ticket #:code "etu"
                        (volume "2022-1" 45)
                        (volume "2022-2" 39)
                        (volume "2023-1" 45)
                        (volume "2023-2" 40)))

(define t6 (make-ticket #:code "viec"
                        (volume "2023" 29)))

(define t7 (make-ticket #:code "catbq"
                        (volume "2023" 51)))

(define t8 (make-ticket #:code "revhe"
                        (volume "2021-1" 36)
                        (volume "2021-2" 38)))

(define t9 (make-ticket #:code "catbq"
                        (volume "2022" 47)))

(define t10 (make-ticket #:code "natgf"
                        (volume "2022-1" 39)
                        (volume "2022-2" 44)
                        (volume "2023-1" 42)
                        (volume "2023-2" 44)))

(define t11 (make-ticket #:code "monb"
                        (volume "2023" 37)))

(define t12 (make-ticket #:code "comfr"
                        (volume "2023" 45)))

(define t13 (make-ticket #:code "con"
                        (volume "2023" 29)))

(define t14 (make-ticket #:code "ecco"
                        (volume "2021" 50)))
                        
(define t15 (make-ticket #:code "collc"
                        (volume "2022" 36)
                        (volume "2023" 31)))

(define t16 (make-ticket #:code "litu"
                        (volume "2022" 32)))

(define t17 (make-ticket #:code "novv"
                        (volume "2022" 41)
                        (volume "2023" 41)))

(define t18 (make-ticket #:code "bulle"
                        (volume "2022" 44)
                        (volume "2023" 43)))

(define t19 (make-ticket #:code "pri"
                        (volume "2023" 33)))

(define t20 (make-ticket #:code "revtho"
                        (volume "2022" 72)))

(define t21 (make-ticket #:code "revspt"
                        (volume "2022" 44)))

(define t22 (make-ticket #:code "feun"
                        (volume "2022-2023 A" 50)))

(define t23 (make-ticket #:code "cissq"
                        (volume "2022" 39)))

(define t24 (make-ticket #:code "ist"
                        (volume "2022" 45)
                        (volume "2023" 42)))

(define t25 (make-ticket #:code "bib"
                        (volume "2022" 53)))

(define t26 (make-ticket #:code "ques"
                        (volume "2023" 30)))

(define t27 (make-ticket #:code "pasq"
                        (volume "2022-2023" 31)))

(define t28 (make-ticket #:code "geof"
                        (volume "2023-1" 40)
                        (volume "2023-2" 44)))

(define t29 (make-ticket #:code "revsr"
                        (volume "2022" 34)
                        (volume "2023" 32)))

(define t30 (make-ticket #:code "revbib"
                        (volume "2022" 52)
                        (volume "2023" 52)))

(define t31 (make-ticket #:code "revtlou"
                        (volume "2022" 49)))

(define t32 (make-ticket #:code "revhe"
                        (volume "2022" 37)
                        (volume "2023" 39)))

(define t33 (make-ticket #:code "revben"
                        (volume "2023" 39)))

(define t34 (make-ticket #:code "bulhb"
                        (volume "2023" 17)))

(define t35 (make-ticket #:code "sciv"
                        (volume "2023" 31)))



(pdf #:filename "tickets-220224"
     t1 t2 t3 t4 t5 t6
     'newpage t7 t8 t9 t10 t11
     'newpage t12 t13 t14 t15 t16
     'newpage t17 t18 t19 t20 t21
     'newpage t22 t23 t24 t25 t26
     'newpage t27 t28 t29 t30 t31
     'newpage t32 t33 t34 t35) 