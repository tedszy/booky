;;; Tickets for March 28, 2020.

#lang racket

(require "booky.rkt")

(start)

(define t1 (make-ticket #:code "letaml"
                        (volume "2019-2021" 25)))
                      
(define t2 (make-ticket #:code "monb"
                        (volume "2021" 43)))
                       
(define t3 (make-ticket #:code "revbib"
                        (volume "2021" 57)))
                        
(define t4 (make-ticket #:code "catbq"
                        (volume "2020" 48)
                        (volume "2021" 47)))

(define t5 (make-ticket #:code "revhe"
                        (volume "2021" 44)))
                       
(define t6 (make-ticket #:code "viec"
                        (volume "2021" 31)))
                        
(define t7 (make-ticket #:code "bib"
                        (volume "2020" 52)))

(define t8 (make-ticket #:code "pasq"
                        (volume "2020" 34)))

(define t9 (make-ticket #:code "feun"
                        (volume "2021" 45)))

(define t10 (make-ticket #:code "pri"
                        (volume "2021" 32)))

(define t11 (make-ticket #:code "maid"
                        (volume "2019" 58)))
                       
(define t12 (make-ticket #:code "ges"
                        (volume "2020-2021" 31)))
                        
(define t13 (make-ticket #:code "litu"
                        (volume "2021" 27)))

(define t14 (make-ticket #:code "ambr"
                        (volume "2021" 38)))

(define t15 (make-ticket #:code "revtlou"
                        (volume "2020" 49)))

(define t16 (make-ticket #:code "revspt"
                        (volume "2020" 49)))

(define t17 (make-ticket #:code "nourt"
                        (volume "2021" 38)))
                       
(define t18 (make-ticket #:code "ire"
                        (volume "2020" 37)))
                        
(define t19 (make-ticket #:code "rel"
                        (volume "2021" 24)))

(define t20 (make-ticket #:code "ques"
                        (volume "2021" 26)))

(define t21 (make-ticket #:code "revtho"
                        (volume "2020" 68)))

(define t22 (make-ticket #:code "comfr"
                        (volume "2021" 42)))

(define t23 (make-ticket #:code "bulle"
                        (volume "2021" 52)))
                       
(define t24 (make-ticket #:code "revsr"
                        (volume "2020" 35)))
                        
(define t25 (make-ticket #:code "unic"
                        (volume "2020-2021" 24)))

(define t26 (make-ticket #:code "chr"
                        (volume "2021" 30)))

(pdf #:filename "tickets-050222"
     t1 t2 t3 t4 t5 t6 'newpage t7 t8 t9 t10 t11 'newpage t12 t13 t14 t15 t16 'newpage t17 t18 t19 t20 t21 'newpage t22 t23 t24 t25 t26)
